from __future__ import annotations

from datetime import timedelta
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from google.cloud import pubsub_v1, storage
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from cards.application.services.card import CardService
from cards.domain.models.card import Card, CardAdd
from cards.infrastructure.repositories.card import CardRepository
from core.auth import require_auth
from core.db import get_db
from core.gcp import get_publisher, get_storage_client
from core.settings import settings
from uuid import UUID, uuid4

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
    return UploadUrlResponse(upload_url=signed_url)


@router.get("/", response_model=List[Card])
async def list_cards(session: AsyncSession = db_session):
    repo = CardRepository(session)
    svc = CardService(repo)
    return await svc.list_cards()


@router.post("/", response_model=Card, status_code=status.HTTP_201_CREATED)
async def add_card(
    payload: CardAdd,
    publisher: Annotated[pubsub_v1.PublisherClient, Depends(get_publisher)],
    session: AsyncSession = db_session,
):
    repo = CardRepository(session)
    svc = CardService(repo)
    card = await svc.add_card(payload)

    return card


@router.get("/{card_id}", response_model=Card)
async def get_card(card_id: UUID, session: AsyncSession = db_session):
    repo = CardRepository(session)
    svc = CardService(repo)
    card = await svc.get_card(card_id)
    if card is None:
        raise HTTPException(status_code=404, detail="card not found")
    return card
