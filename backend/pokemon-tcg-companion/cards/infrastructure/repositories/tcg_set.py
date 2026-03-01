from __future__ import annotations

from typing import Optional

from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from cards.domain.models import TcgSet, TcgSetAdd
from cards.domain.repositories import AbstractTcgSetRepository


class TcgSetRepository(AbstractTcgSetRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def upsert(self, set_data: TcgSetAdd) -> TcgSet:
        stmt = (
            pg_insert(TcgSet)
            .values(**set_data.model_dump())
            .on_conflict_do_update(
                index_elements=["tcg_id"],
                set_={"name": set_data.name, "year": set_data.year},
            )
            .returning(TcgSet)
        )
        result = await self.session.execute(
            stmt, execution_options={"populate_existing": True}
        )
        await self.session.commit()
        return result.scalars().one()

    async def get_by_tcg_id(self, tcg_id: str) -> Optional[TcgSet]:
        result = await self.session.execute(
            select(TcgSet).where(TcgSet.tcg_id == tcg_id)
        )
        return result.scalar_one_or_none()
