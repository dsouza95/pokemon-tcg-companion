from __future__ import annotations

import functools
from typing import Callable

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel

from cards.domain.models import RefCardRead, TcgSetRead

# Models that have no API routes but are used via ElectricSQL sync and must
# appear in the generated OpenAPI schema so the frontend types stay in sync.
EXTRA_SCHEMAS: list[type[BaseModel]] = [RefCardRead, TcgSetRead]


def openapi_schema(app: FastAPI) -> dict:
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(title=app.title, version=app.version, routes=app.routes)
    for model in EXTRA_SCHEMAS:
        schema.setdefault("components", {}).setdefault("schemas", {})[
            model.__name__
        ] = model.model_json_schema()
    app.openapi_schema = schema
    return app.openapi_schema


def bind(app: FastAPI) -> Callable[[], dict]:
    return functools.partial(openapi_schema, app)
