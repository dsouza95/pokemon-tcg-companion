"""Pub/Sub test utilities."""

import base64

from pydantic import BaseModel

from core.pubsub_model import PubSubEnvelope, PubSubMessage


def create_pubsub_message(payload: BaseModel) -> PubSubEnvelope:
    """
    Create a Pub/Sub push message envelope for testing.

    Args:
        payload: The payload to encode

    Returns:
        A PubSubEnvelope ready for testing
    """
    payload_json = payload.model_dump_json()
    encoded_data = base64.b64encode(payload_json.encode()).decode()

    return PubSubEnvelope(
        message=PubSubMessage(
            data=encoded_data,
            messageId="test-message-123",
            publishTime="2024-01-01T00:00:00Z",
        ),
        subscription="projects/test-project/subscriptions/test-sub",
    )
