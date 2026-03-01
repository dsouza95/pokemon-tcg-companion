from __future__ import annotations

from collections.abc import Sequence
from typing import Optional
from uuid import UUID

from cards.domain.models import CardAdd, CardRead, CardUpdate
from cards.domain.repositories import AbstractCardRepository


class CardService:
    def __init__(self, repo: AbstractCardRepository) -> None:
        self.repo = repo

    async def add_card(self, card: CardAdd) -> CardRead:
        return await self.repo.add(card)

    async def get_card(self, id: UUID) -> Optional[CardRead]:
        return await self.repo.get(id)

    async def update_card(self, id: UUID, card: CardUpdate) -> CardRead:
        return await self.repo.update(id, card)

    async def list_cards(self) -> Sequence[CardRead]:
        return await self.repo.list()

    async def delete_card(self, id: UUID) -> None:
        return await self.repo.delete(id)
