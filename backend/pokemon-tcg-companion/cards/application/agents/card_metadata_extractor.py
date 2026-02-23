from pydantic import BaseModel, field_validator
from pydantic_ai import Agent

from core.settings import settings


class CardMetadata(BaseModel):
    tcg_local_id: str
    name: str
    set_id: str

    @field_validator("tcg_local_id")
    @classmethod
    def extract_local_id(cls, v: str) -> str:
        """The AI might return the full card notation (e.g. '158/149'); extract the local part."""
        return v.split("/")[0].strip()

    @field_validator("set_id")
    @classmethod
    def normalize_set_id(cls, v: str) -> str:
        return v.lower()


class CardMetadataExtractor(Agent[None, CardMetadata]):
    """Agent for extracting structured metadata from a card image."""

    def __init__(self):
        super().__init__(
            settings.default_agent_model,
            output_type=CardMetadata,
            system_prompt=(
                "You are a helpful assistant for extracting structured metadata from a Pokemon TCG card image. "
                "Given an image of a card, you will extract the following information:\n"
                "- tcg_local_id: The unique sequential number for the card within its set. It is always on the bottom of the card, more to one of the corners. It will always be in the format tcg_local_id/number_of_cards_in_set (i.e. 4/102, with 4 being the local id and 102 being the total number of cards in the set).\n"
                "- name: The name of the card. The name of the card will usually be the name of the Pokémon shown in the card, but it can also be an Item, Energy, Trainer or other more rare kinds. This is always on the top of the card along with other information that we don't want to extract like HP, type and optionally stage.\n"
                "- set_id: The identifier for the set this card belongs to. It is usually a short string of letters and optionally numbers that identifies the set.\n"
                "If any of this information cannot be determined from the image, return an empty string for that field."
            ),
        )
