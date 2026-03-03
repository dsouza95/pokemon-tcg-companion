from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from pydantic import BaseModel
from pydantic_ai import Agent, ModelRetry, RunContext
from sqlalchemy.ext.asyncio import AsyncSession

from cards.application.services import RefCardService
from cards.infrastructure.repositories import RefCardRepository
from core.settings.agents import settings


class MatchResult(BaseModel):
    id: UUID


@dataclass
class CardMatcherAgentDeps:
    session: AsyncSession


card_matcher_agent = Agent(
    settings.default_agent_model,
    deps_type=CardMatcherAgentDeps,
    output_type=MatchResult,
    system_prompt=(
        "You are a Pokemon TCG card matching assistant. Given a card image:\n"
        "1. Extract the card's name, year, and tcg_local_id\n"
        "- tcg_local_id: The unique sequential number for the card within its set. It is always on the bottom of the card, more to one of the corners. It will always be in the format tcg_local_id/number_of_cards_in_set (i.e. 4/102, with 4 being the local id and 102 being the total number of cards in the set).\n"
        "- name: The name of the card. The name of the card will usually be the name of the Pokémon shown in the card, but it can also be an Item, Energy, Trainer or other more rare kinds. This is always on the top of the card along with other information that we don't want to extract like HP, type and optionally stage.\n"
        "- year: The copyright year printed at the bottom of the card (e.g. from '©2023 Pokémon' extract 2023, from '©1995-2023 Pokémon' extract 2023). If a range of years is shown, use the most recent one.\n"
        "If any of this information cannot be determined from the image, return an empty string for string fields or 0 for the year field."
        "2. Call find_match_candidates with the extracted metadata\n"
        "3. Return the id of the best matching candidate\n"
        "You MUST return the id of one of the provided candidates — do not fabricate an id."
    ),
)


@card_matcher_agent.tool
async def find_match_candidates(
    ctx: RunContext[CardMatcherAgentDeps],
    name: str,
    year: int,
    local_id: str,
) -> list[dict]:
    """Find candidate reference cards matching metadata extracted from the card image."""
    service = RefCardService(RefCardRepository(ctx.deps.session))
    candidates = await service.find_match_candidates(
        name=name, year=year, local_id=local_id
    )
    if not candidates:
        raise ModelRetry(
            f"No candidates found for name={name!r}, year={year!r}, local_id={local_id!r}. "
            "Double-check your extracted metadata and try again with corrected values."
        )
    return [c.model_dump(mode="json") for c in candidates]
