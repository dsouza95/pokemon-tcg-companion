from __future__ import annotations

import os
from typing import AsyncGenerator, Awaitable, Callable, TypeVar
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from core.settings import settings

_engine: AsyncEngine | None = None
_session_maker: async_sessionmaker | None = None

T = TypeVar("T")


def _normalize_async_url(url: str) -> str:
    """Normalize a database URL to use asyncpg.

    Handles common cases when using hosted providers like Neon:
    - 'postgresql://' or 'postgres://' → 'postgresql+asyncpg://'
    - 'sslmode=require' (libpq syntax) → 'ssl=require' (asyncpg syntax)
    - 'channel_binding=require' stripped (asyncpg does not support this param)
    """
    url = url.replace("postgres://", "postgresql://", 1)
    if "postgresql+asyncpg://" not in url:
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)

    parsed = urlparse(url)
    params = parse_qs(parsed.query, keep_blank_values=True)
    if "sslmode" in params:
        params["ssl"] = params.pop("sslmode")
    params.pop("channel_binding", None)
    url = urlunparse(parsed._replace(query=urlencode(params, doseq=True)))

    return url


def get_engine() -> AsyncEngine:
    global _engine
    if _engine is None:
        url = _normalize_async_url(
            os.environ.get("DATABASE_URL", settings.database_url)
        )
        _engine = create_async_engine(url, future=True, echo=False)

    return _engine


def get_session_maker() -> async_sessionmaker:
    global _session_maker
    if _session_maker is None:
        _session_maker = async_sessionmaker(get_engine(), expire_on_commit=False)

    return _session_maker


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    maker = get_session_maker()
    async with maker() as session:
        yield session


async def with_session(fn: Callable[..., Awaitable[T]], *args, **kwargs) -> T:
    maker = get_session_maker()
    async with maker() as session:
        return await fn(session, *args, **kwargs)
