from __future__ import annotations

from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


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


class CardAdd(CardBase):
    pass


class CardUpdate(SQLModel):
    ref_card_id: Optional[UUID] = None
    user_id: Optional[str] = None
    image_path: Optional[str] = None
