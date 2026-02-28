import json
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI
from google.cloud import pubsub_v1, storage
from google.oauth2 import service_account

from core.settings import settings


def _get_gcp_credentials() -> service_account.Credentials | None:
    """Build GCP credentials from JSON setting if provided, otherwise use ADC.

    In production, set GOOGLE_APPLICATION_CREDENTIALS_JSON to the service account
    JSON content. Locally, leave it unset and use GOOGLE_APPLICATION_CREDENTIALS
    (file path) or `gcloud auth application-default login` as usual.
    """
    if not settings.google_application_credentials_json:
        return None

    info = json.loads(settings.google_application_credentials_json.get_secret_value())
    return service_account.Credentials.from_service_account_info(
        info,
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    credentials = _get_gcp_credentials()
    app.state.storage_client = storage.Client(credentials=credentials)
    app.state.publisher = pubsub_v1.PublisherClient(credentials=credentials)
    # Use a long-lived client with no read timeout for streaming sync
    app.state.sync_http_client = httpx.AsyncClient(
        timeout=httpx.Timeout(timeout=20.0, read=None)
    )
    try:
        yield
    finally:
        await app.state.sync_http_client.aclose()
