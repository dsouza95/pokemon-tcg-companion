"""Mock factories for external services."""

from os import urandom
from typing import Protocol, Tuple, TypeVar, cast
from unittest.mock import AsyncMock, MagicMock

T = TypeVar("T")


class AgentResult(Protocol[T]):
    output: T


class AgentInstance(Protocol[T]):
    async def run(self) -> AgentResult[T]: ...


def _generate_random_bytes() -> bytes:
    return urandom(1024)


def create_mock_storage_client(
    blob_content: bytes = _generate_random_bytes(),
) -> MagicMock:
    """
    Create a mock GCS storage client

    Args:
        blob_content: The content to return from the blob download

    Returns:
        A MagicMock configured as a storage.Client
    """
    mock_blob = MagicMock()
    mock_blob.download_as_bytes.return_value = blob_content
    mock_blob.generate_signed_url.return_value = "https://test-url.com"

    mock_bucket = MagicMock()
    mock_bucket.blob.return_value = mock_blob

    mock_storage_client = MagicMock()
    mock_storage_client.bucket.return_value = mock_bucket

    return mock_storage_client


def create_mock_pubsub_publisher() -> MagicMock:
    """
    Create a mock Pub/Sub publisher client.

    Returns:
        A MagicMock configured as a pubsub_v1.PublisherClient
    """
    mock_publisher = MagicMock()
    mock_publisher.topic_path.return_value = "projects/test/topics/test"
    mock_publisher.publish.return_value.result.return_value = "msg-123"

    return mock_publisher


def create_mock_agent(result: T) -> Tuple[MagicMock, AgentInstance[T]]:
    """
    Create a mock agent that returns the provided result.

    Args:
        result: The result to return from the agent

    Returns:
        A tuple of (mock_agent_class, mock_agent_instance) to use with patch
    """

    mock_agent_result = MagicMock()
    mock_agent_result.output = result

    mock_agent_instance = AsyncMock()
    mock_agent_instance.run.return_value = mock_agent_result

    mock_agent_class = MagicMock()
    mock_agent_class.return_value = mock_agent_instance

    return mock_agent_class, cast(AgentInstance[T], mock_agent_instance)
