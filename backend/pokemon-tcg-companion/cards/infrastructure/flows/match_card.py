"""Prefect flow for matching an uploaded card image to a reference card."""

from __future__ import annotations

import asyncio
from uuid import UUID

from google.cloud import storage
from prefect import flow, task
from pydantic_ai import BinaryContent
from pydantic_ai.models.google import GoogleModelSettings
from sqlalchemy.ext.asyncio import AsyncSession

from cards.application.agents import (
    CardMetadata,
    CardMetadataExtractor,
    RefCardMatcher,
)
from cards.application.services import CardService, RefCardService
from cards.domain.models import Card, CardUpdate, RefCard
from cards.infrastructure.repositories import CardRepository, RefCardRepository
from core.db import with_session
from core.flows import with_logfire
from core.settings import settings

FLOW_NAME = "match_card_flow"


@task(
    retries=settings.default_flow_retries,
    retry_delay_seconds=settings.default_flow_retry_delay_seconds,
)
async def download_card(card_path: str) -> bytes:
    storage_client = storage.Client()
    bucket = storage_client.bucket(settings.gcp_bucket)
    blob = bucket.blob(card_path)

    return await asyncio.to_thread(blob.download_as_bytes)


@task(
    retries=settings.default_flow_retries,
    retry_delay_seconds=settings.default_flow_retry_delay_seconds,
)
async def extract_card_metadata(card_bytes: bytes) -> CardMetadata:
    agent = CardMetadataExtractor()
    # TODO: media_type should ideally be inferred from the file extension in the image path
    result = await agent.run(
        [
            "Extract metadata from the following pokémon card:",
            BinaryContent(data=card_bytes, media_type="image/jpeg"),
        ],
        model_settings=GoogleModelSettings(
            google_thinking_config={"include_thoughts": True}
        ),
    )

    return result.output


@task(
    retries=settings.default_flow_retries,
    retry_delay_seconds=settings.default_flow_retry_delay_seconds,
)
async def find_match_candidates(metadata: CardMetadata) -> list[RefCard]:
    async def _query(session: AsyncSession) -> list[RefCard]:
        service = RefCardService(RefCardRepository(session))
        return await service.find_match_candidates(
            name=metadata.name,
            set_id=metadata.set_id,
            local_id=metadata.tcg_local_id,
        )

    return await with_session(_query)


@task(
    retries=settings.default_flow_retries,
    retry_delay_seconds=settings.default_flow_retry_delay_seconds,
)
async def match_card(card_bytes: bytes, candidates: list[RefCard]) -> RefCard:
    agent = RefCardMatcher()
    result = await agent.run(
        [
            "Match the provided pokémon card to one of the candidates:\n",
            f"Candidates: {[c.model_dump(mode='json') for c in candidates]}\n",
            "Image: ",
            BinaryContent(data=card_bytes, media_type="image/jpeg"),
        ],
        model_settings=GoogleModelSettings(
            google_thinking_config={"include_thoughts": True}
        ),
    )

    candidates_by_id = {c.id: c for c in candidates}
    matched = candidates_by_id.get(result.output.id)
    if matched is None:
        raise ValueError(
            f"Agent returned id {result.output.id!r} which is not among the candidate ids: "
            f"{list(candidates_by_id)}"
        )

    return matched


async def _update_card_with_match(
    session: AsyncSession, card_id: str, matched_card: RefCard
):
    repo = CardRepository(session)
    service = CardService(repo)

    card = await service.update_card(
        UUID(card_id), CardUpdate(ref_card_id=matched_card.id)
    )
    await session.commit()

    return card


@task(
    retries=settings.default_flow_retries,
    retry_delay_seconds=settings.default_flow_retry_delay_seconds,
)
async def update_card_with_match(card_id: str, matched_card: RefCard) -> Card:
    return await with_session(_update_card_with_match, card_id, matched_card)


@flow(name=FLOW_NAME, log_prints=True)
@with_logfire(pydantic_ai=True)
async def match_card_flow(card_id: str, image_path: str):
    card_bytes = await download_card(image_path)
    card_metadata = await extract_card_metadata(card_bytes)
    candidates = await find_match_candidates(card_metadata)
    if len(candidates) == 0:
        raise ValueError(
            f"No candidates found for extracted metadata: "
            f"name={card_metadata.name!r}, set_id={card_metadata.set_id!r}, "
            f"tcg_local_id={card_metadata.tcg_local_id!r}"
        )

    matched_ref_card = await match_card(card_bytes, candidates)
    card = await update_card_with_match(card_id, matched_ref_card)

    return {
        "card": card.model_dump(),
        "candidates": [c.model_dump() for c in candidates],
        "matched_ref_card": matched_ref_card.model_dump(),
    }


__all__ = ["FLOW_NAME", "match_card_flow"]
