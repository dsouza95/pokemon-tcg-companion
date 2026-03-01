from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Optional
from uuid import UUID

from cards.domain.models import CardAdd, CardRead, CardUpdate


class AbstractCardRepository(ABC):
    @abstractmethod
    async def add(self, card: CardAdd) -> CardRead: ...

    @abstractmethod
    async def get(self, id: UUID) -> Optional[CardRead]: ...

    @abstractmethod
    async def list(self) -> Sequence[CardRead]: ...

    @abstractmethod
    async def update(self, id: UUID, card: CardUpdate) -> CardRead: ...

    @abstractmethod
    async def delete(self, id: UUID) -> None: ...
