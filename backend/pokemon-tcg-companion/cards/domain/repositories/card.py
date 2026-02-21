from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Optional
from uuid import UUID

from cards.domain.models.card import Card, CardAdd, CardUpdate


class AbstractCardRepository(ABC):
    @abstractmethod
    async def add(self, card: CardAdd) -> Card: ...

    @abstractmethod
    async def get(self, id: UUID) -> Optional[Card]: ...

    @abstractmethod
    async def list(self) -> Sequence[Card]: ...

    @abstractmethod
    async def update(self, id: UUID, card: CardUpdate) -> Card: ...
