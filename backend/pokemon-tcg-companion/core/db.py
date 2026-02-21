from __future__ import annotations

from typing import AsyncGenerator, Awaitable, Callable, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from core.settings import settings

engine = create_async_engine(settings.database_url, future=True, echo=False)
AsyncSessionMaker = async_sessionmaker(engine, expire_on_commit=False)

T = TypeVar("T")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionMaker() as session:
        yield session


async def with_session(fn: Callable[..., Awaitable[T]], *args, **kwargs) -> T:
    async with AsyncSessionMaker() as session:
        return await fn(session, *args, **kwargs)
