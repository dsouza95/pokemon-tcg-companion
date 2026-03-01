from __future__ import annotations

from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class TcgSetBase(SQLModel):
    tcg_id: str
    name: str
    year: Optional[int] = None


class TcgSet(TcgSetBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    tcg_id: str = Field(index=True, unique=True)
    year: Optional[int] = Field(default=None, index=True)


class TcgSetRead(TcgSetBase):
    id: UUID


class TcgSetAdd(TcgSetBase):
    pass
