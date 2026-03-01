import pytest_asyncio

from cards.application.services import RefCardService, TcgSetService
from cards.domain.models import RefCard, RefCardAdd, TcgSet, TcgSetAdd
from cards.infrastructure.repositories import RefCardRepository, TcgSetRepository


@pytest_asyncio.fixture
async def tcg_set(session) -> TcgSet:
    """Create a Base Set TcgSet in the test DB."""
    return await TcgSetService(TcgSetRepository(session)).upsert_set(
        TcgSetAdd(tcg_id="base1", name="Base Set", year=1999)
    )


@pytest_asyncio.fixture
async def ref_card(session, tcg_set: TcgSet) -> RefCard:
    service = RefCardService(RefCardRepository(session))
    return await service.add_card(
        RefCardAdd(
            name="Charizard",
            tcg_id="base1-4",
            tcg_local_id="4",
            image_url="https://assets.tcgdex.net/en/base/base1/4/high.png",
            set_id=tcg_set.id,
        )
    )
