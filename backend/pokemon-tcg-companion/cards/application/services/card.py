from __future__ import annotations

from collections.abc import Sequence
from typing import Optional
from uuid import UUID

from cards.domain.models import Card, CardAdd, CardUpdate
from cards.domain.repositories import AbstractCardRepository


class CardService:
    def __init__(self, repo: AbstractCardRepository) -> None:
        self.repo = repo

    async def add_card(self, card: CardAdd) -> Card:
        return await self.repo.add(card)

    async def get_card(self, id: UUID) -> Optional[Card]:
        return await self.repo.get(id)

    async def update_card(self, id: UUID, card: CardUpdate) -> Card:
        return await self.repo.update(id, card)

    async def list_cards(self) -> Sequence[Card]:
        return await self.repo.list()
