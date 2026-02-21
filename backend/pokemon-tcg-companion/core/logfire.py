import logfire
from fastapi import FastAPI


def setup_logfire(
    *, pydantic_ai: bool = False, fastapi_app: FastAPI | None = None
) -> None:
    logfire.configure()

    if pydantic_ai:
        logfire.instrument_pydantic_ai()

    if fastapi_app is not None:
        logfire.instrument_fastapi(fastapi_app)
