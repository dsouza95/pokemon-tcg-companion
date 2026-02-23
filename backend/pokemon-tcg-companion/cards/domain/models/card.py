from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

from cards.domain.models.ref_card import RefCard, RefCardRead


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
    ref_card: Optional[RefCard] = Relationship(
        sa_relationship_kwargs={"lazy": "noload"}
    )


class CardRead(SQLModel):
    id: UUID
    ref_card_id: Optional[UUID] = None
    user_id: str
    image_path: str
    ref_card: Optional[RefCardRead] = None


class CardAdd(CardBase):
    pass


class CardUpdate(SQLModel):
    ref_card_id: Optional[UUID] = None
    user_id: Optional[str] = None
    image_path: Optional[str] = None
