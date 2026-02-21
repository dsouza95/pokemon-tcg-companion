from contextlib import asynccontextmanager

from fastapi import FastAPI
from google.cloud import pubsub_v1, storage


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.storage_client = storage.Client()
    app.state.publisher = pubsub_v1.PublisherClient()
    yield
