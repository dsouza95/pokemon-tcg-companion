from __future__ import annotations

from collections.abc import Sequence
from typing import Optional, cast
from uuid import UUID

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import ColumnElement
from sqlmodel import select

from cards.domain.models import RefCard, RefCardAdd, RefCardUpdate
from cards.domain.repositories import AbstractRefCardRepository


class RefCardRepository(AbstractRefCardRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, card: RefCardAdd) -> RefCard:
        new_card = RefCard(**card.model_dump())
        self.session.add(new_card)
        await self.session.commit()
        return new_card

    async def get(self, id: UUID) -> Optional[RefCard]:
        return await self.session.get(RefCard, id)

    async def list(self) -> Sequence[RefCard]:
        q = await self.session.execute(select(RefCard))
        return q.scalars().all()

    async def update(self, id: UUID, card: RefCardUpdate) -> RefCard:
        values = card.model_dump(exclude_unset=True)
        stmt = (
            update(RefCard)
            .where(cast(ColumnElement[bool], RefCard.id == id))
            .values(values)
            .returning(RefCard)
        )
        result = await self.session.execute(stmt)
        updated_card = result.scalar_one()
        await self.session.commit()
        return updated_card
