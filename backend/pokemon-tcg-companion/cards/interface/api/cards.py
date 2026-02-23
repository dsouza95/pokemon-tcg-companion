from __future__ import annotations

import asyncio
import json
from datetime import timedelta
from typing import Annotated, List
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from google.cloud import pubsub_v1, storage
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from cards.application.services import CardService
from cards.domain.models import Card, CardAdd, CardRead
from cards.infrastructure.repositories import CardRepository
from core.auth import require_auth
from core.db import get_db
from core.gcp import get_publisher, get_storage_client
from core.settings import settings

router = APIRouter(
    prefix="/cards",
    tags=["cards"],
    dependencies=[Depends(require_auth)],
)

db_session = Depends(get_db)


class CreateCardSignedUploadUrl(BaseModel):
    filename: str
    content_type: str


class UploadUrlResponse(BaseModel):
    upload_url: str
    image_path: str


class CreateCardPayload(BaseModel):
    image_path: str


CARD_CREATED_TOPIC = "card-created"


@router.post("/upload-url", response_model=UploadUrlResponse)
async def create_upload_url(
    payload: CreateCardSignedUploadUrl,
    storage_client: Annotated[storage.Client, Depends(get_storage_client)],
):
    object_name = f"cards/{uuid4()}"
    bucket = storage_client.bucket(settings.gcp_bucket)
    blob = bucket.blob(object_name)
    signed_url = blob.generate_signed_url(
        version="v4",
        expiration=timedelta(minutes=15),
        method="PUT",
        content_type=payload.content_type,
    )
    return UploadUrlResponse(upload_url=signed_url, image_path=object_name)


@router.get("", response_model=List[CardRead])
async def list_cards(session: AsyncSession = db_session):
    repo = CardRepository(session)
    svc = CardService(repo)
    return await svc.list_cards()


@router.post("", response_model=Card, status_code=status.HTTP_201_CREATED)
async def add_card(
    payload: CreateCardPayload,
    auth_payload: Annotated[dict, Depends(require_auth)],
    publisher: Annotated[pubsub_v1.PublisherClient, Depends(get_publisher)],
    session: AsyncSession = db_session,
):
    user_id = auth_payload["sub"]
    card_add = CardAdd(
        image_path=payload.image_path,
        user_id=user_id,
    )
    repo = CardRepository(session)
    svc = CardService(repo)

    card = await svc.add_card(card_add)

    topic_payload = json.dumps(card.model_dump(mode="json")).encode("utf-8")
    topic_path = publisher.topic_path(settings.gcp_pubsub_project, CARD_CREATED_TOPIC)
    future = await asyncio.to_thread(publisher.publish, topic_path, topic_payload)
    await asyncio.to_thread(future.result)

    return card


@router.get("/{card_id}", response_model=CardRead)
async def get_card(card_id: UUID, session: AsyncSession = db_session):
    repo = CardRepository(session)
    svc = CardService(repo)
    card = await svc.get_card(card_id)
    if card is None:
        raise HTTPException(status_code=404, detail="card not found")
    return card
