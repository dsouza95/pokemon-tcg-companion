import os
import tempfile
from unittest.mock import patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from prefect.testing.utilities import prefect_test_harness
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import SQLModel

from core.db import get_db
from flows import FLOWS
from main import app
from tests.utils.mocks import create_mock_pubsub_publisher, create_mock_storage_client

# create a temp file at import time to avoid using blocking
# file APIs inside async fixtures
temp_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
temp_file.close()


@pytest.fixture(scope="session", autouse=True)
def prefect_test_fixture():
    """
    Enable Prefect test mode for all tests.

    This fixture runs flows against a temporary local SQLite database,
    isolating tests from your production Prefect environment.
    """
    with prefect_test_harness():
        yield


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
        app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="session")
async def async_engine():
    url = f"sqlite+aiosqlite:///{temp_file.name}"
    engine = create_async_engine(url, future=True)
    async with engine.begin() as conn:
        await conn.execute(text("PRAGMA foreign_keys=ON"))
        await conn.run_sync(SQLModel.metadata.create_all)
    yield engine
    await engine.dispose()
    try:
        os.unlink(temp_file.name)
    except OSError:
        pass


@pytest_asyncio.fixture
async def session(async_engine):
    # Ensure a clean schema for each test to avoid committed
    # state leaking between tests. Dropping and recreating
    # tables per-test is simple and reliable for SQLite test DBs.
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)

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


@pytest.fixture
def run_deployment_inline():
    """Patch run_deployment to execute the flow directly in-process.

    Replaces the Prefect work pool scheduling with a direct flow call,
    while keeping full Prefect orchestration (task states, retries, etc.).
    Add new flows to FLOWS as they are created.
    """

    async def fake_run_deployment(name, parameters=None, **_):
        flow_name = name.split("/")[0]
        return await FLOWS[flow_name](**(parameters or {}))

    with patch("core.flows.arun_deployment", new=fake_run_deployment):
        yield


@pytest_asyncio.fixture(autouse=True)
async def mock_flow_db(session):
    """Mock database connections in flows to use test database."""
    from contextlib import asynccontextmanager

    @asynccontextmanager
    async def mock_session_maker():
        yield session

    with patch("core.db.AsyncSessionMaker", return_value=mock_session_maker()):
        yield
