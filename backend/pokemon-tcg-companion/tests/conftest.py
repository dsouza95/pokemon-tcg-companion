from unittest.mock import patch
from urllib.parse import urlparse, urlunparse

import asyncpg
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from prefect.testing.utilities import prefect_test_harness
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import SQLModel

from core.auth import require_auth
from core.db import get_db, normalize_async_url
from flows import FLOWS
from main import app
from tests.utils.mocks import create_mock_pubsub_publisher, create_mock_storage_client

DATABASE_SYNC_URL = (
    "postgresql://postgres:postgres@localhost:5432/pokemon_tcg_companion_db_test"
)


async def _ensure_test_db() -> None:
    parsed = urlparse(DATABASE_SYNC_URL)
    db_name = parsed.path.lstrip("/")
    admin_dsn = urlunparse(parsed._replace(path="/postgres"))

    conn = await asyncpg.connect(dsn=admin_dsn)
    try:
        exists = await conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1", db_name
        )
        if not exists:
            await conn.execute(f'CREATE DATABASE "{db_name}"')
    finally:
        await conn.close()


@pytest.fixture(scope="session", autouse=True)
def prefect_test_mode():
    """
    Enable Prefect test mode for all tests.

    This fixture runs flows against a temporary local database,
    isolating tests from your production Prefect environment.
    """
    with prefect_test_harness():
        yield


@pytest.fixture(scope="session", autouse=True)
def mock_auth():
    """Override require_auth with a fake payload."""
    payload = {"sub": "user_test"}

    app.dependency_overrides[require_auth] = lambda: payload
    yield payload
    app.dependency_overrides.pop(require_auth, None)


@pytest_asyncio.fixture(scope="session")
async def async_engine():
    await _ensure_test_db()
    engine = create_async_engine(normalize_async_url(DATABASE_SYNC_URL), future=True)
    async with engine.begin() as conn:
        # Drop all tables with raw SQL to avoid asyncpg's limitation with
        # multiple sequential queries inside run_sync
        for table in reversed(SQLModel.metadata.sorted_tables):
            await conn.execute(text(f'DROP TABLE IF EXISTS "{table.name}" CASCADE'))
        await conn.run_sync(SQLModel.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def client(session):
    """
    Create an AsyncClient with database session override.

    Individual tests can add their own mocks as needed.
    """

    async def get_test_session():
        yield session

    app.dependency_overrides[get_db] = get_test_session

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            yield client
    finally:
        app.dependency_overrides.pop(get_db, None)


@pytest_asyncio.fixture
async def session(async_engine):
    # TRUNCATE all tables per-test for fast, reliable isolation. Avoids the
    # asyncpg issue with drop_all's per-table has_table checks inside run_sync.
    tables = ", ".join(f'"{t.name}"' for t in SQLModel.metadata.sorted_tables)
    async with async_engine.begin() as conn:
        await conn.execute(text(f"TRUNCATE {tables} RESTART IDENTITY CASCADE"))

    async_session_local = async_sessionmaker(async_engine, expire_on_commit=False)
    async with async_session_local() as session:
        yield session
        await session.rollback()


@pytest.fixture
def mock_publisher():
    """Mock the Pub/Sub publisher dependency."""
    from core.gcp import get_publisher

    mock = create_mock_pubsub_publisher()
    app.dependency_overrides[get_publisher] = lambda: mock

    yield mock

    app.dependency_overrides.pop(get_publisher, None)


@pytest.fixture
def mock_storage():
    """Mock the storage client dependency and any storage.Client instantiation."""
    from core.gcp import get_storage_client

    mock = create_mock_storage_client()
    app.dependency_overrides[get_storage_client] = lambda: mock

    with patch("google.cloud.storage.Client", return_value=mock):
        yield mock

    app.dependency_overrides.pop(get_storage_client, None)


@pytest_asyncio.fixture
async def prefect_flow(session):
    """
    Patches both the deployment runner and the DB session maker so flows
    execute synchronously against the test DB without a work pool.
    """
    from contextlib import asynccontextmanager

    @asynccontextmanager
    async def mock_session_maker():
        yield session

    async def fake_run_deployment(name, parameters=None, **_):
        flow_name = name.split("/")[0]
        return await FLOWS[flow_name](**(parameters or {}))

    with patch("core.db.get_session_maker", return_value=mock_session_maker):
        with patch("core.flows.arun_deployment", new=fake_run_deployment):
            yield
