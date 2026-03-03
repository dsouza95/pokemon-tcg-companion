"""Integration tests for card API routes."""

from __future__ import annotations

import base64
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4

import pytest
from pydantic_ai.exceptions import UnexpectedModelBehavior

from cards.application.agents.card_matcher import MatchResult, card_matcher_agent
from cards.application.services import CardService
from cards.domain.models import CardAdd, CardRead, MatchingStatus
from cards.infrastructure.repositories import CardRepository
from tests.utils.mocks import create_mock_storage_client
from tests.utils.pubsub import create_pubsub_message


@pytest.fixture
def mock_storage_with_card_image():
    mock_client = create_mock_storage_client(blob_content=b"fake-image-bytes")
    mock_client.bucket().blob().content_type = "image/jpeg"

    async def _fake_get_storage_client():
        return mock_client

    with patch(
        "cards.infrastructure.flows.match_card._get_storage_client",
        new=_fake_get_storage_client,
    ):
        yield mock_client


class TestCardsAPI:
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_list_cards_empty(self, client):
        """Returns an empty list when no cards exist."""
        response = await client.get("/cards")
        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_list_cards(self, session, client):
        """Returns all persisted cards."""
        svc = CardService(CardRepository(session))
        await svc.add_card(CardAdd(image_path="cards/test.jpg", user_id="user_test"))
        await svc.add_card(CardAdd(image_path="cards/test2.jpg", user_id="user_test"))

        response = await client.get("/cards")
        assert response.status_code == 200
        cards = response.json()
        assert len(cards) == 2

        assert cards[0]["user_id"] == "user_test"
        assert cards[0]["image_path"] == "cards/test.jpg"
        assert cards[0]["matching_status"] == MatchingStatus.pending

        assert cards[1]["user_id"] == "user_test"
        assert cards[1]["image_path"] == "cards/test2.jpg"
        assert cards[1]["matching_status"] == MatchingStatus.pending

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_add_card(self, client, mock_publisher):
        """Adding a card creates a DB record and publishes a card-created event."""
        mock_publisher.publish.assert_not_called()

        response = await client.post(
            "/cards",
            json={"image_path": "cards/test.jpg"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["image_path"] == "cards/test.jpg"
        assert data["user_id"] == "user_test"
        assert data["matching_status"] == MatchingStatus.pending
        mock_publisher.publish.assert_called_once()

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_get_card(self, session, client):
        """Returns an existing card by ID."""
        svc = CardService(CardRepository(session))
        card = await svc.add_card(
            CardAdd(image_path="cards/test.jpg", user_id="user_test")
        )

        response = await client.get(f"/cards/{card.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(card.id)
        assert data["image_path"] == "cards/test.jpg"
        assert data["user_id"] == "user_test"
        assert data["matching_status"] == MatchingStatus.pending

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_get_card_not_found(self, client):
        """Returns 404 for an unknown card ID."""
        response = await client.get(f"/cards/{uuid4()}")
        assert response.status_code == 404

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_delete_card(self, session, client):
        """Deletes a card and returns 204."""
        svc = CardService(CardRepository(session))
        card = await svc.add_card(
            CardAdd(image_path="cards/test.jpg", user_id="user_test")
        )

        response = await client.delete(f"/cards/{card.id}")
        assert response.status_code == 204

        response = await client.get(f"/cards/{card.id}")
        assert response.status_code == 404

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.usefixtures("mock_storage")
    async def test_create_upload_url(self, client):
        """Returns a signed upload URL and a GCS image path."""
        response = await client.post(
            "/cards/upload-url",
            json={"filename": "charizard.jpg", "content_type": "image/jpeg"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("upload_url")
        assert data.get("image_path")

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.usefixtures("mock_storage_with_card_image")
    @pytest.mark.usefixtures("prefect_flow")
    async def test_card_match(
        self,
        session,
        client,
        mock_publisher,
        ref_card,
    ):
        """Full E2E: card created → Pub/Sub webhook → match_card flow → card matched.
        Agent is mocked to prevent calling providers.
        """
        mock_result = MagicMock()
        mock_result.output = MatchResult(id=ref_card.id)

        with patch.object(
            card_matcher_agent, "run", AsyncMock(return_value=mock_result)
        ):
            # Step 1: Create the card via the API
            create_response = await client.post(
                "/cards",
                json={"image_path": "cards/test-charizard.jpg"},
            )
            assert create_response.status_code == 201
            card_data = create_response.json()
            card_id = card_data["id"]
            assert card_data["matching_status"] == MatchingStatus.pending
            mock_publisher.publish.assert_called_once()

            # Step 2: Simulate the Pub/Sub webhook callback
            card_payload = CardRead.model_validate(card_data)
            pubsub_message = create_pubsub_message(payload=card_payload)

            webhook_response = await client.post(
                "/cards/webhooks/card-created",
                json=pubsub_message.model_dump(by_alias=True),
            )
            assert webhook_response.status_code == 200
            assert webhook_response.json()["status"] == "success"
            assert webhook_response.json()["card_id"] == card_id

            # Step 3: Verify the flow ran and matched the card in the database
            svc = CardService(CardRepository(session))
            updated_card = await svc.get_card(UUID(card_id))
            assert updated_card is not None
            assert updated_card.matching_status == MatchingStatus.matched
            assert updated_card.ref_card_id == ref_card.id

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.usefixtures("mock_publisher")
    @pytest.mark.usefixtures("mock_storage_with_card_image")
    @pytest.mark.usefixtures("prefect_flow")
    async def test_card_matching_fails_with_unexpected_model_behavior(
        self, session, client
    ):
        """Card matching fails gracefully when model raises UnexpectedModelBehavior (i.e. failed to find any candidates with tool)."""
        with patch.object(
            card_matcher_agent,
            "run",
            AsyncMock(side_effect=UnexpectedModelBehavior("Retry limit reached")),
        ):
            # Step 1: Create the card
            create_response = await client.post(
                "/cards",
                json={"image_path": "cards/test-hallucination.jpg"},
            )
            assert create_response.status_code == 201
            card_id = create_response.json()["id"]

            # Step 2: Trigger matching via webhook
            card_payload = CardRead.model_validate(create_response.json())
            pubsub_message = create_pubsub_message(payload=card_payload)

            with pytest.raises(UnexpectedModelBehavior):
                await client.post(
                    "/cards/webhooks/card-created",
                    json=pubsub_message.model_dump(by_alias=True),
                )

            # Step 3: Verify the card status is 'failed'
            svc = CardService(CardRepository(session))
            updated_card = await svc.get_card(UUID(card_id))
            assert updated_card is not None
            assert updated_card.matching_status == MatchingStatus.failed
            assert updated_card.ref_card_id is None

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.usefixtures("mock_publisher")
    @pytest.mark.usefixtures("mock_storage_with_card_image")
    @pytest.mark.usefixtures("prefect_flow")
    @pytest.mark.usefixtures("ref_card")
    async def test_card_matching_fails_when_matcher_hallucinates(self, session, client):
        """Card matching fails gracefully when the agent returns an ID not in the database."""
        mock_result = MagicMock()
        mock_result.output = MatchResult(id=uuid4())

        with patch.object(
            card_matcher_agent, "run", AsyncMock(return_value=mock_result)
        ):
            create_response = await client.post(
                "/cards",
                json={"image_path": "cards/test-matcher-hallucination.jpg"},
            )
            card_id = create_response.json()["id"]

            card_payload = CardRead.model_validate(create_response.json())
            pubsub_message = create_pubsub_message(payload=card_payload)

            with pytest.raises(ValueError, match="does not exist in the database"):
                await client.post(
                    "/cards/webhooks/card-created",
                    json=pubsub_message.model_dump(by_alias=True),
                )

            svc = CardService(CardRepository(session))
            updated_card = await svc.get_card(UUID(card_id))
            assert updated_card is not None
            assert updated_card.matching_status == MatchingStatus.failed
            assert updated_card.ref_card_id is None

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.usefixtures("mock_publisher")
    @pytest.mark.usefixtures("mock_storage_with_card_image")
    @pytest.mark.usefixtures("prefect_flow")
    async def test_card_matching_fails_on_agent_error(self, session, client):
        """Card matching fails gracefully when the agent raises an error (e.g. invalid response format)."""
        with patch.object(
            card_matcher_agent,
            "run",
            AsyncMock(side_effect=ValueError("Simulated LLM error")),
        ):
            create_response = await client.post(
                "/cards",
                json={"image_path": "cards/test-agent-error.jpg"},
            )
            card_id = create_response.json()["id"]

            card_payload = CardRead.model_validate(create_response.json())
            pubsub_message = create_pubsub_message(payload=card_payload)

            with pytest.raises(ValueError, match="Simulated LLM error"):
                await client.post(
                    "/cards/webhooks/card-created",
                    json=pubsub_message.model_dump(by_alias=True),
                )

            svc = CardService(CardRepository(session))
            updated_card = await svc.get_card(UUID(card_id))
            assert updated_card is not None
            assert updated_card.matching_status == MatchingStatus.failed


@pytest.mark.asyncio
@pytest.mark.integration
async def test_webhook_rejects_invalid_payload(client):
    """Webhook returns 422 for a Pub/Sub message whose payload is not a valid Card."""
    invalid_message = {
        "message": {
            "data": base64.b64encode(b'{"invalid": "data"}').decode(),
            "messageId": "test-123",
            "publishTime": "2024-01-01T00:00:00Z",
        },
        "subscription": "projects/test/subscriptions/test",
    }
    response = await client.post("/cards/webhooks/card-created", json=invalid_message)
    assert response.status_code == 422


@pytest.mark.asyncio
@pytest.mark.integration
async def test_webhook_rejects_invalid_signature(client):
    """Webhook returns 401 for a Pub/Sub message whose signature is invalid."""
    # We enable verification by patching settings in the auth module
    with (
        patch("core.auth.settings.pubsub_audience", "test-audience"),
        patch("core.auth.settings.pubsub_service_account_email") as mock_email,
    ):
        mock_email.get_secret_value.return_value = "test-service-account@example.com"

        # Test 1: Missing Authorization header should return 401
        response = await client.post("/cards/webhooks/card-created", json={})
        assert response.status_code == 401
        assert response.json()["detail"] == "Unauthorized"

        # Test 2: Invalid token (id_token.verify_oauth2_token fails) should return 401
        with patch(
            "core.auth.id_token.verify_oauth2_token",
            side_effect=ValueError("Invalid token"),
        ):
            response = await client.post(
                "/cards/webhooks/card-created",
                json={},
                headers={"Authorization": "Bearer invalid-token"},
            )
            assert response.status_code == 401
            assert response.json()["detail"] == "Unauthorized"
