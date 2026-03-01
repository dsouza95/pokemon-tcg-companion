from __future__ import annotations

from cards.domain.models import TcgSet, TcgSetAdd
from cards.domain.repositories import AbstractTcgSetRepository


class TcgSetService:
    def __init__(self, repo: AbstractTcgSetRepository) -> None:
        self.repo = repo

    async def upsert_set(self, set_data: TcgSetAdd) -> TcgSet:
        return await self.repo.upsert(set_data)
