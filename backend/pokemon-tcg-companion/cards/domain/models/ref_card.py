from __future__ import annotations

from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class RefCardBase(SQLModel):
    tcg_id: str
    tcg_local_id: str
    name: str
    image_url: Optional[str] = None
    set_id: str
    set_name: str


class RefCard(RefCardBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    tcg_id: str = Field(index=True, unique=True)
    tcg_local_id: str = Field(index=True)
    set_id: str = Field(index=True)


class RefCardAdd(RefCardBase):
    pass


class RefCardUpdate(SQLModel):
    tcg_id: Optional[str] = None
    tcg_local_id: Optional[str] = None
    name: Optional[str] = None
    image_url: Optional[str] = None
    set_id: Optional[str] = None
    set_name: Optional[str] = None
