from __future__ import annotations

from collections.abc import Sequence
from typing import Optional
from uuid import UUID

from cards.domain.models import RefCard, RefCardAdd, RefCardUpdate
from cards.domain.repositories import AbstractRefCardRepository
from core.rrf import reciprocal_rank_fusion


class RefCardService:
    def __init__(self, repo: AbstractRefCardRepository) -> None:
        self.repo = repo

    async def add_card(self, card: RefCardAdd) -> RefCard:
        return await self.repo.add(card)

    async def get_card(self, id: UUID) -> Optional[RefCard]:
        return await self.repo.get(id)

    async def update_card(self, id: UUID, card: RefCardUpdate) -> RefCard:
        return await self.repo.update(id, card)

    async def list_cards(self) -> Sequence[RefCard]:
        return await self.repo.list()

    async def upsert_many_cards(self, cards: Sequence[RefCardAdd]) -> None:
        return await self.repo.upsert_many(cards)

    async def find_match_candidates(
        self, name: str, year: int, local_id: str, limit: int = 10
    ) -> list[RefCard]:
        # TODO: this can be optimized by doing the three searches in parallel,
        # but its tricky since we cant reuse the same session across threads
        year_local = (
            await self.repo.search_by_year_and_local_id(year, local_id) if year else []
        )
        year_name = await self.repo.search_by_year_and_name(year, name) if year else []
        local_name = await self.repo.search_by_local_id_and_name(local_id, name)

        return reciprocal_rank_fusion(
            [year_local, year_name, local_name],
            limit=limit,
            weights=[2.0, 1.0, 1.0],
        )
