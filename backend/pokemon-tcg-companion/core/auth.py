from __future__ import annotations

from clerk_backend_api import Clerk
from clerk_backend_api.security.types import AuthenticateRequestOptions
from fastapi import HTTPException, Request

from core.settings import settings

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
