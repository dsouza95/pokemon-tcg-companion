import pytest

from cards.application.services import TcgSetService
from cards.domain.models import TcgSetAdd
from cards.infrastructure.repositories import TcgSetRepository


@pytest.mark.asyncio
async def test_upsert_creates_set(session):
    svc = TcgSetService(TcgSetRepository(session))

    tcg_set = await svc.upsert_set(
        TcgSetAdd(tcg_id="base1", name="Base Set", year=1999)
    )

    assert tcg_set.id is not None
    assert tcg_set.tcg_id == "base1"
    assert tcg_set.name == "Base Set"
    assert tcg_set.year == 1999


@pytest.mark.asyncio
async def test_upsert_updates_existing_set(session):
    svc = TcgSetService(TcgSetRepository(session))

    first = await svc.upsert_set(TcgSetAdd(tcg_id="base1", name="Base Set", year=1999))
    second = await svc.upsert_set(
        TcgSetAdd(tcg_id="base1", name="Base Set Updated", year=2000)
    )

    assert second.id == first.id
    assert second.name == "Base Set Updated"
    assert second.year == 2000


@pytest.mark.asyncio
async def test_upsert_different_sets_get_different_ids(session):
    svc = TcgSetService(TcgSetRepository(session))

    base = await svc.upsert_set(TcgSetAdd(tcg_id="base1", name="Base Set", year=1999))
    jungle = await svc.upsert_set(TcgSetAdd(tcg_id="jungle", name="Jungle", year=1999))

    assert base.id != jungle.id
