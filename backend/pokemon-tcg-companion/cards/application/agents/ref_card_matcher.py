from uuid import UUID

from pydantic import BaseModel
from pydantic_ai import Agent

from core.settings import settings


class MatchResult(BaseModel):
    id: UUID


class RefCardMatcher(Agent[None, MatchResult]):
    """Agent for matching a card image to one of the existing reference cards."""

    def __init__(self):
        super().__init__(
            settings.default_agent_model,
            output_type=MatchResult,
            system_prompt=(
                "You are a helpful assistant for matching a Pokemon TCG card image to one of the existing reference cards. "
                "You will be given an image of a card and a list of candidates. Each candidate has an id, name, set_id, tcg_local_id, and set_name. "
                "Identify which candidate best matches the card image by comparing:\n"
                "- name: The name of the Pokémon or card type at the top of the card.\n"
                "- tcg_local_id: The sequential number at the bottom of the card, in the format local_id/total (e.g. 4/102).\n"
                "- set_id: The short identifier for the set this card belongs to.\n"
                "Return ONLY the id of the best matching candidate. "
                "You MUST return the id of one of the provided candidates — do not provide a new id."
            ),
        )
