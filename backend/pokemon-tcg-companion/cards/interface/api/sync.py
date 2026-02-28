import httpx
from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from starlette.background import BackgroundTask

from core.auth import require_auth
from core.settings import settings

router = APIRouter(dependencies=[Depends(require_auth)])
SYNC_PROXY_TIMEOUT = 20.0


def _get_electric_connection_url(request: Request, table_name: str):
    base_url = settings.electric_service_url

    params = dict(request.query_params)
    params["table"] = table_name
    params["source_id"] = settings.electric_source_id
    params["secret"] = settings.electric_source_secret.get_secret_value()

    return f"{base_url}?{httpx.QueryParams(params)}"


def _get_headers(request: Request) -> dict:
    # Only forward specific headers to avoid Electric rejection
    allowed_headers = ["accept", "if-none-match"]
    return {k: v for k, v in request.headers.items() if k.lower() in allowed_headers}


@router.api_route(
    "/sync/{table_name}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"]
)
async def sync_proxy(request: Request, table_name: str):
    url = _get_electric_connection_url(request, table_name)
    headers = _get_headers(request)
    client = request.app.state.sync_http_client

    response = await client.send(
        client.build_request(
            method=request.method,
            url=url,
            headers=headers,
            content=request.stream(),
        ),
        stream=True,
    )

    response_headers = {
        h: response.headers[h]
        for h in [
            "electric-offset",
            "electric-handle",
            "electric-schema",
            "electric-cursor",
            "electric-up-to-date",
        ]
        if h in response.headers
    }

    return StreamingResponse(
        response.aiter_bytes(),
        status_code=response.status_code,
        headers=response_headers,
        background=BackgroundTask(response.aclose),
        media_type=response.headers.get("content-type"),
    )
