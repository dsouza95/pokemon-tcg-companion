from fastapi import Request
from google.cloud import pubsub_v1, storage


def get_storage_client(request: Request) -> storage.Client:
    return request.app.state.storage_client


def get_publisher(request: Request) -> pubsub_v1.PublisherClient:
    return request.app.state.publisher
