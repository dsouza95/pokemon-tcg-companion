from __future__ import annotations

from collections.abc import Sequence
from typing import Optional, cast
from uuid import UUID

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import ColumnElement
from sqlmodel import select

from cards.domain.models.card import Card, CardAdd, CardUpdate
from cards.domain.repositories.card import AbstractCardRepository


class CardRepository(AbstractCardRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, card: CardAdd) -> Card:
        new_card = Card(**card.model_dump())
        self.session.add(new_card)
        await self.session.commit()
        return new_card

    async def get(self, id: UUID) -> Optional[Card]:
        return await self.session.get(Card, id)

    async def list(self) -> Sequence[Card]:
        q = await self.session.execute(select(Card))
        return q.scalars().all()

    async def update(self, id: UUID, card: CardUpdate) -> Card:
        values = card.model_dump(exclude_unset=True)
        stmt = (
            update(Card)
            .where(cast(ColumnElement[bool], Card.id == id))
            .values(values)
            .returning(Card)
        )
        result = await self.session.execute(stmt)
        updated_card = result.scalar_one()
        await self.session.commit()
        return updated_card
