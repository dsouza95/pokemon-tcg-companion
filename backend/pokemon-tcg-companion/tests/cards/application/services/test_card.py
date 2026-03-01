import pytest

from cards.application.services import CardService
from cards.domain.models import CardAdd, CardUpdate, RefCard
from cards.infrastructure.repositories import CardRepository


@pytest.mark.asyncio
async def test_service(session, ref_card: RefCard):
    repo = CardRepository(session)
    svc = CardService(repo)

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
