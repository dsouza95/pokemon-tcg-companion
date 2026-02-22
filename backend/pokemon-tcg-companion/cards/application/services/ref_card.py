from __future__ import annotations

from collections.abc import Sequence
from typing import Optional
from uuid import UUID

from cards.domain.models import RefCard, RefCardAdd, RefCardUpdate
from cards.domain.repositories import AbstractRefCardRepository


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
