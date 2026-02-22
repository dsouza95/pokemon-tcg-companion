import pytest

from cards.application.services import RefCardService
from cards.domain.models import RefCardAdd, RefCardUpdate
from cards.infrastructure.repositories import RefCardRepository


@pytest.mark.asyncio
async def test_basic_operations(session):
    repo = RefCardRepository(session)
    svc = RefCardService(repo)

    card = await svc.add_card(
        RefCardAdd(
            name="Charizard",
            tcg_id="base1-1",
            tcg_local_id="1",
            image_url="https://assets.tcgdex.net/en/base/base1/1/high.png",
            set_id="base1",
            set_name="Base Set",
        )
    )

    updated_card = await svc.update_card(
        card.id,
        RefCardUpdate(
            tcg_id="base1-4",
            tcg_local_id="4",
            image_url="https://assets.tcgdex.net/en/base/base1/4/high.png",
        ),
    )

    assert updated_card.tcg_id == "base1-4"
    assert updated_card.tcg_local_id == "4"
    assert (
        updated_card.image_url == "https://assets.tcgdex.net/en/base/base1/4/high.png"
    )

    # Retrieve and verify card data is persisted
    retrieved_card = await svc.get_card(card.id)
    assert retrieved_card is not None
    assert retrieved_card.id == card.id
    assert retrieved_card.name == "Charizard"
    assert retrieved_card.tcg_id == "base1-4"
    assert retrieved_card.tcg_local_id == "4"
    assert retrieved_card.set_id == "base1"
    assert retrieved_card.set_name == "Base Set"
    assert (
        retrieved_card.image_url == "https://assets.tcgdex.net/en/base/base1/4/high.png"
    )

    # List cards and verify retrieved card is the only one
    cards = await svc.list_cards()
    assert cards == [retrieved_card]


@pytest.mark.asyncio
async def test_upsert_many_cards(session):
    repo = RefCardRepository(session)
    svc = RefCardService(repo)

    cards = [
        RefCardAdd(
            name="Charizard",
            tcg_id="base1-4",
            tcg_local_id="4",
            set_id="base1",
            set_name="Base Set",
        ),
        RefCardAdd(
            name="Blastoise",
            tcg_id="base1-2",
            tcg_local_id="2",
            set_id="base1",
            set_name="Base Set",
        ),
    ]
    await svc.upsert_many_cards(cards)

    all_cards = await svc.list_cards()
    assert len(all_cards) == 2
    assert {c.tcg_id for c in all_cards} == {"base1-4", "base1-2"}

    # Re-upsert with updated names — should update, not duplicate
    updated = [
        RefCardAdd(
            name="Charizard EX",
            tcg_id="base1-4",
            tcg_local_id="4",
            set_id="base1",
            set_name="Base Set",
        ),
        RefCardAdd(
            name="Blastoise EX",
            tcg_id="base1-2",
            tcg_local_id="2",
            set_id="base1",
            set_name="Base Set",
        ),
    ]
    await svc.upsert_many_cards(updated)

    all_cards = await svc.list_cards()
    assert len(all_cards) == 2
    assert {c.name for c in all_cards} == {"Charizard EX", "Blastoise EX"}
