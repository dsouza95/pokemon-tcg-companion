from __future__ import annotations

from collections.abc import Sequence
from typing import Optional, Self, cast
from uuid import UUID

from sqlalchemy import func, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import ColumnElement, Select
from sqlmodel import select

from cards.domain.models import RefCard, RefCardAdd, RefCardUpdate
from cards.domain.repositories import AbstractRefCardRepository


class RefCardQuery:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._stmt: Select = select(RefCard)

    def by_year(self, year: int) -> Self:
        self._stmt = self._stmt.where(
            cast(ColumnElement[bool], RefCard.set_year == year)
        )
        return self

    def by_local_id(self, local_id: str) -> Self:
        self._stmt = self._stmt.where(
            cast(ColumnElement[bool], RefCard.tcg_local_id == local_id)
        )
        return self

    def by_name(self, name: str, threshold: float = 0.3, limit: int = 20) -> Self:
        similarity = func.similarity(RefCard.name, name)
        self._stmt = (
            self._stmt.where(cast(ColumnElement[bool], similarity > threshold))
            .order_by(similarity.desc())
            .limit(limit)
        )
        return self

    async def all(self) -> Sequence[RefCard]:
        result = await self._session.execute(self._stmt)
        return result.scalars().all()


class RefCardRepository(AbstractRefCardRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def query(self) -> RefCardQuery:
        return RefCardQuery(self.session)

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

    async def upsert_many(self, cards: Sequence[RefCardAdd]) -> None:
        if not cards:
            return

        upserted_tcg_ids = set()
        data = []
        for card in cards:
            data.append(card.model_dump())
            upserted_tcg_ids.add(card.tcg_id)

        stmt = pg_insert(RefCard).values(data)
        stmt = stmt.on_conflict_do_update(
            index_elements=["tcg_id"],
            set_={col: stmt.excluded[col] for col in data[0] if col != "tcg_id"},
        )
        await self.session.execute(stmt)
        await self.session.commit()

        for obj in self.session.identity_map.values():
            if isinstance(obj, RefCard) and obj.tcg_id in upserted_tcg_ids:
                self.session.expire(obj)

    async def search_by_year_and_local_id(
        self, year: int, local_id: str
    ) -> Sequence[RefCard]:
        return await self.query().by_year(year).by_local_id(local_id).all()

    async def search_by_year_and_name(
        self, year: int, name: str, limit: int = 20
    ) -> Sequence[RefCard]:
        return await self.query().by_year(year).by_name(name, limit=limit).all()

    async def search_by_local_id_and_name(
        self, local_id: str, name: str, limit: int = 20
    ) -> Sequence[RefCard]:
        return await self.query().by_local_id(local_id).by_name(name, limit=limit).all()
