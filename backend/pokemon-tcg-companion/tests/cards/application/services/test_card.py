import pytest

from cards.application.services import CardService, RefCardService
from cards.domain.models import CardAdd, CardUpdate, RefCardAdd
from cards.infrastructure.repositories import CardRepository, RefCardRepository


@pytest.mark.asyncio
async def test_service(session):
    repo = CardRepository(session)
    svc = CardService(repo)

    ref_card_repo = RefCardRepository(session)
    ref_card_svc = RefCardService(ref_card_repo)

    ref_card = await ref_card_svc.add_card(
        RefCardAdd(
            name="Charizard",
            tcg_id="base1-1",
            tcg_local_id="1",
            image_url="https://assets.tcgdex.net/en/base/base1/1/high.png",
            set_id="base1",
            set_name="Base Set",
        )
    )
    card = await svc.add_card(
        CardAdd(
            ref_card_id=ref_card.id,
            image_path="cards/charizard.png",
            user_id="user_test123",
        )
    )

    updated_card = await svc.update_card(
        card.id,
        CardUpdate(
            image_path="cards/charizard-updated.png",
        ),
    )

    assert updated_card.image_path == "cards/charizard-updated.png"

    # Retrieve and verify card data is persisted
    retrieved_card = await svc.get_card(card.id)
    assert retrieved_card is not None
    assert retrieved_card.id == card.id
    assert retrieved_card.ref_card_id == ref_card.id
    assert retrieved_card.image_path == "cards/charizard-updated.png"

    # List cards and verify retrieved card is the only one
    cards = await svc.list_cards()
    assert cards == [retrieved_card]

    # Delete the card
    await svc.delete_card(card.id)
    deleted_card = await svc.get_card(card.id)
    assert deleted_card is None
