import functools
from collections.abc import Callable
from typing import Any

from prefect.deployments import arun_deployment, run_deployment

from core.logfire import setup_logfire
from core.settings import settings


def get_deployment_name(flow_name: str) -> str:
    return f"{flow_name}/{settings.prefect_deployment}"


def with_logfire(
    *,
    pydantic_ai: bool = False,
) -> Any:
    """Decorator to configure Logfire for a Prefect flow."""

    def decorator(f: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(f)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            setup_logfire(pydantic_ai=pydantic_ai)
            return await f(*args, **kwargs)

        return wrapper

    return decorator


__all__ = ["arun_deployment", "get_deployment_name", "run_deployment", "with_logfire"]
