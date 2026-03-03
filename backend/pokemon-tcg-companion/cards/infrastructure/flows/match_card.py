"""Prefect flow for matching an uploaded card image to a reference card."""

from __future__ import annotations

import asyncio
from uuid import UUID

from google.cloud import storage
from prefect import flow, task
from prefect_gcp import GcpCredentials
from pydantic_ai import BinaryContent
from pydantic_ai.models.google import GoogleModelSettings
from sqlalchemy.ext.asyncio import AsyncSession

from cards.application.agents import CardMatcherAgentDeps, card_matcher_agent
from cards.application.services import CardService, RefCardService
from cards.domain.models import CardRead, CardUpdate, MatchingStatus, RefCard
from cards.infrastructure.repositories import CardRepository, RefCardRepository
from core.db import with_session
from core.flows import with_logfire
from core.settings.prefect import settings

FLOW_NAME = "match_card_flow"


async def _get_storage_client() -> storage.Client:
    try:
        gcp_credentials_block = await GcpCredentials.load("gcp-credentials")  # type: ignore[misc] this is a false-positive
        return gcp_credentials_block.get_cloud_storage_client()
    except ValueError:
        return storage.Client()


@task(
    retries=settings.default_flow_retries,
    retry_delay_seconds=settings.default_flow_retry_delay_seconds,
)
async def download_card(card_path: str) -> tuple[bytes, str]:
    storage_client = await _get_storage_client()
    bucket = storage_client.bucket(settings.gcp_bucket)
    blob = bucket.blob(card_path)

    return await asyncio.to_thread(blob.download_as_bytes), blob.content_type


async def _run_card_matcher_agent(
    session: AsyncSession, card_bytes: bytes, card_mimetype: str
) -> RefCard:
    result = await card_matcher_agent.run(
        [
            "Match the provided Pokémon card image to one of the reference cards:",
            BinaryContent(data=card_bytes, media_type=card_mimetype),
        ],
        deps=CardMatcherAgentDeps(session=session),
        model_settings=GoogleModelSettings(
            google_thinking_config={"include_thoughts": True}
        ),
    )

    service = RefCardService(RefCardRepository(session))
    matched = await service.get_card(result.output.id)
    if matched is None:
        raise ValueError(
            f"Agent returned id {result.output.id!r} which does not exist in the database"
        )
    return matched


@task(
    retries=settings.default_flow_retries,
    retry_delay_seconds=settings.default_flow_retry_delay_seconds,
)
async def run_card_matcher_agent(card_bytes: bytes, card_mimetype: str) -> RefCard:
    return await with_session(_run_card_matcher_agent, card_bytes, card_mimetype)


async def _update_card_with_match(
    session: AsyncSession, card_id: str, matched_card: RefCard
):
    service = CardService(CardRepository(session))

    card = await service.update_card(
        UUID(card_id),
        CardUpdate(ref_card_id=matched_card.id, matching_status=MatchingStatus.matched),
    )

    return card


async def _update_card_with_failure(session: AsyncSession, card_id: str):
    service = CardService(CardRepository(session))
    await service.update_card(
        UUID(card_id), CardUpdate(matching_status=MatchingStatus.failed)
    )


@task(
    retries=settings.default_flow_retries,
    retry_delay_seconds=settings.default_flow_retry_delay_seconds,
)
async def update_card_with_match(card_id: str, matched_card: RefCard) -> CardRead:
    return await with_session(_update_card_with_match, card_id, matched_card)


@flow(name=FLOW_NAME, log_prints=True)
@with_logfire(pydantic_ai=True)
async def match_card_flow(card_id: str, image_path: str):
    try:
        card_bytes, card_mimetype = await download_card(image_path)
        matched_ref_card = await run_card_matcher_agent(card_bytes, card_mimetype)
        card = await update_card_with_match(card_id, matched_ref_card)
    except Exception:
        await with_session(_update_card_with_failure, card_id)
        raise

    return {
        "card": card.model_dump(),
        "matched_ref_card": matched_ref_card.model_dump(),
    }


__all__ = ["FLOW_NAME", "match_card_flow"]
