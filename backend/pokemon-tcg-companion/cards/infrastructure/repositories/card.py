from __future__ import annotations

from collections.abc import Sequence
from typing import Optional, cast
from uuid import UUID

from sqlalchemy import delete, desc, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import QueryableAttribute
from sqlalchemy.sql import ColumnElement
from sqlmodel import select

from cards.domain.models import Card, CardAdd, CardRead, CardUpdate
from cards.domain.repositories import AbstractCardRepository


class CardRepository(AbstractCardRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, card: CardAdd) -> CardRead:
        new_card = Card(**card.model_dump())
        self.session.add(new_card)
        await self.session.commit()
        return CardRead.model_validate(new_card)

    async def get(self, id: UUID) -> Optional[CardRead]:
        card = await self.session.get(Card, id)
        return CardRead.model_validate(card) if card else None

    async def list(self) -> Sequence[CardRead]:
        stmt = select(Card).order_by(
            desc(cast(QueryableAttribute, Card.ref_card_id).is_(None))
        )
        cards = (await self.session.execute(stmt)).scalars().all()
        return [CardRead.model_validate(card) for card in cards]

    async def update(self, id: UUID, card: CardUpdate) -> CardRead:
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
        return CardRead.model_validate(updated_card)

    async def delete(self, id: UUID) -> None:
        stmt = delete(Card).where(cast(ColumnElement[bool], Card.id == id))
        await self.session.execute(stmt)
        await self.session.commit()
