from __future__ import annotations

from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class CardBase(SQLModel):
    tcg_id: Optional[str] = None
    name: Optional[str] = None
    image_path: str
    user_id: str


class Card(CardBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: str = Field(index=True)


class CardAdd(CardBase):
    pass


class CardUpdate(SQLModel):
    tcg_id: Optional[str] = None
    name: Optional[str] = None
    image_path: Optional[str] = None
