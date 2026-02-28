from __future__ import annotations

import logging

from clerk_backend_api import Clerk
from clerk_backend_api.security.types import AuthenticateRequestOptions
from fastapi import Header, HTTPException, Request
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

from core.settings import settings

logger = logging.getLogger(__name__)

clerk = Clerk(bearer_auth=settings.clerk_secret_key)


async def require_auth(request: Request) -> dict:
    state = await clerk.authenticate_request_async(
        request,
        AuthenticateRequestOptions(
            authorized_parties=[settings.clerk_authorized_party]
        ),
    )
    if not state.is_signed_in or state.payload is None:
        raise HTTPException(status_code=401, detail=state.message)

    return state.payload


def verify_pubsub_token(authorization: str = Header(default="")) -> None:
    """Verify the bearer token attached by Pub/Sub to push requests."""
    if not settings.pubsub_audience or not settings.pubsub_service_account_email:
        return
    
    try:
        token = authorization.removeprefix("Bearer ")
        claim = id_token.verify_oauth2_token(token, google_requests.Request(), audience=settings.pubsub_audience)
    except Exception:
        logger.warning("Pub/Sub token verification failed", exc_info=True)
        raise HTTPException(status_code=401, detail="Unauthorized")

    email = claim.get("email")
    email_verified = claim.get("email_verified")

    if not email_verified:
        logger.warning("Pub/Sub token email is not verified (email=%s)", email)
        raise HTTPException(status_code=401, detail="Unauthorized")

    if email != settings.pubsub_service_account_email:
        logger.warning(
            "Pub/Sub token email mismatch: got %r, expected %r",
            email,
            settings.pubsub_service_account_email,
        )
        raise HTTPException(status_code=401, detail="Unauthorized")
