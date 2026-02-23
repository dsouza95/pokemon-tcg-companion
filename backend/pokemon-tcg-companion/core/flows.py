import functools
import inspect
from collections.abc import Callable
from typing import Any

import logfire
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
            sig = inspect.signature(f)
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()
            with logfire.span(f.__name__, **bound.arguments):
                result = await f(*args, **kwargs)
                logfire.info(f"{f.__name__} completed", result=result)
                return result

        return wrapper

    return decorator


__all__ = ["arun_deployment", "get_deployment_name", "run_deployment", "with_logfire"]
