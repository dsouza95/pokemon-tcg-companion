import pytest

from cards.application.services.card import CardService
from cards.domain.models.card import CardAdd, CardUpdate
from cards.infrastructure.repositories.card import CardRepository


@pytest.mark.asyncio
async def test_service(session):
    repo = CardRepository(session)
    svc = CardService(repo)

    card = await svc.add_card(
        CardAdd(
            name="Charizard",
            tcg_id="base1-1",
            image_path="https://assets.tcgdex.net/en/base/base1/1/high.png",
            user_id="user_test123",
        )
    )

    updated_card = await svc.update_card(
        card.id,
        CardUpdate(
            tcg_id="base1-4",
            image_path="https://assets.tcgdex.net/en/base/base1/4/high.png",
        ),
    )

    assert updated_card.tcg_id == "base1-4"
    assert (
        updated_card.image_path == "https://assets.tcgdex.net/en/base/base1/4/high.png"
    )

    # Retrieve and verify card data is persisted
    retrieved_card = await svc.get_card(card.id)
    assert retrieved_card is not None
    assert retrieved_card.id == card.id
    assert retrieved_card.name == "Charizard"
    assert retrieved_card.tcg_id == "base1-4"
    assert (
        retrieved_card.image_path == "https://assets.tcgdex.net/en/base/base1/4/high.png"
    )

    # List cards and verify retrieved card is the only one
    cards = await svc.list_cards()
    assert cards == [retrieved_card]
