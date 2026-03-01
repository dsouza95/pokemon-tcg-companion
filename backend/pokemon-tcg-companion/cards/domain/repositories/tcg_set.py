from abc import ABC, abstractmethod
from typing import Optional

from cards.domain.models import TcgSet, TcgSetAdd


class AbstractTcgSetRepository(ABC):
    @abstractmethod
    async def upsert(self, set_data: TcgSetAdd) -> TcgSet: ...

    @abstractmethod
    async def get_by_tcg_id(self, tcg_id: str) -> Optional[TcgSet]: ...
