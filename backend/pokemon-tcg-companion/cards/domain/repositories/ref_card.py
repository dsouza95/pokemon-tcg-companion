from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Optional
from uuid import UUID

from cards.domain.models import RefCard, RefCardAdd, RefCardUpdate


class AbstractRefCardRepository(ABC):
    @abstractmethod
    async def add(self, card: RefCardAdd) -> RefCard: ...

    @abstractmethod
    async def get(self, id: UUID) -> Optional[RefCard]: ...

    @abstractmethod
    async def list(self) -> Sequence[RefCard]: ...

    @abstractmethod
    async def update(self, id: UUID, card: RefCardUpdate) -> RefCard: ...

    @abstractmethod
    async def upsert_many(self, cards: Sequence[RefCardAdd]) -> None: ...

    @abstractmethod
    async def search_by_year_and_local_id(
        self, year: int, local_id: str
    ) -> Sequence[RefCard]: ...

    @abstractmethod
    async def search_by_year_and_name(
        self, year: int, name: str, limit: int = 20
    ) -> Sequence[RefCard]: ...

    @abstractmethod
    async def search_by_local_id_and_name(
        self, local_id: str, name: str, limit: int = 20
    ) -> Sequence[RefCard]: ...
