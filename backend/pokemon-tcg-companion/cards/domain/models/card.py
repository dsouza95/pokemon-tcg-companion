import enum
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import AutoString, Field, Relationship, SQLModel

from cards.domain.models.ref_card import RefCard


class MatchingStatus(str, enum.Enum):
    pending = "pending"
    matched = "matched"
    failed = "failed"


class CardBase(SQLModel):
    ref_card_id: Optional[UUID] = None
    user_id: str
    image_path: str


class Card(CardBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    ref_card_id: Optional[UUID] = Field(
        foreign_key="refcard.id", default=None, nullable=True, index=True
    )
    user_id: str = Field(index=True)
    matching_status: MatchingStatus = Field(
        default=MatchingStatus.pending, sa_type=AutoString
    )
    ref_card: Optional[RefCard] = Relationship(
        sa_relationship_kwargs={"lazy": "noload"}
    )


class CardRead(SQLModel):
    id: UUID
    ref_card_id: Optional[UUID]
    user_id: str
    image_path: str
    matching_status: MatchingStatus


class CardAdd(CardBase):
    pass


class CardUpdate(SQLModel):
    ref_card_id: Optional[UUID] = None
    user_id: Optional[str] = None
    image_path: Optional[str] = None
    matching_status: Optional[MatchingStatus] = None
