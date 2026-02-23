from __future__ import annotations

from typing import AsyncGenerator, Awaitable, Callable, TypeVar
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from core.settings import settings


def _normalize_async_url(url: str) -> str:
    """Normalize a database URL to use asyncpg.

    Handles two common cases when using hosted providers like Neon:
    - 'postgresql://' or 'postgres://' → 'postgresql+asyncpg://'
    - 'sslmode=require' (libpq syntax) → 'ssl=require' (asyncpg syntax)
    """
    url = url.replace("postgres://", "postgresql://", 1)
    if "postgresql+asyncpg://" not in url:
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)

    parsed = urlparse(url)
    params = parse_qs(parsed.query, keep_blank_values=True)
    if "sslmode" in params:
        params["ssl"] = params.pop("sslmode")
        url = urlunparse(parsed._replace(query=urlencode(params, doseq=True)))

    return url


engine = create_async_engine(_normalize_async_url(settings.database_url), future=True, echo=False)
AsyncSessionMaker = async_sessionmaker(engine, expire_on_commit=False)

T = TypeVar("T")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionMaker() as session:
        yield session


async def with_session(fn: Callable[..., Awaitable[T]], *args, **kwargs) -> T:
    async with AsyncSessionMaker() as session:
        return await fn(session, *args, **kwargs)
