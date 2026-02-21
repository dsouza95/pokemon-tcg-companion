"""
Pydantic schemas for Google Cloud Pub/Sub messages.
"""

from __future__ import annotations

import base64
import json
from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T", bound=BaseModel)


class PubSubMessage(BaseModel):
    """Pub/Sub message structure."""

    data: str
    message_id: str = Field(alias="messageId")
    publish_time: str = Field(alias="publishTime")

    def decode_data(self, model: type[T]) -> T:
        decoded = base64.b64decode(self.data).decode("utf-8")
        payload_dict = json.loads(decoded)
        return model.model_validate(payload_dict)


class PubSubEnvelope(BaseModel, Generic[T]):
    """Pub/Sub push subscription envelope."""

    message: PubSubMessage
    subscription: str

    def get_payload(self, model: type[T]) -> T:
        return self.message.decode_data(model)
