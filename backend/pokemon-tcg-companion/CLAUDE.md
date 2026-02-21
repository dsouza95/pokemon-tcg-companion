# Backend — Pokemon TCG Companion

## Stack

- **Python 3.14**, FastAPI (async), SQLModel + SQLAlchemy 2.0, Alembic
- **Prefect 3** for background flows/tasks
- **PydanticAI** for AI agents
- **Google Cloud** — Storage (manuals), Pub/Sub (event fan-out)
- **uv** (package management), **ruff** (lint/format), **pyright** (types), **pytest-asyncio**

## Commands

```bash
uv run pytest                  # run tests
uv run pyright                 # type check
uv run ruff check --fix .      # lint
uv run ruff format .           # format
uv run alembic upgrade head    # apply migrations
uv run alembic revision --autogenerate -m "<description>"  # new migration
```

Pre-commit runs ruff and pyright automatically on commit.

## Architecture — Domain-Driven Design

Each domain (e.g. `cards/`) follows strict layering:

```
cards/
  domain/          # models, abstract repositories — no infra imports
  application/     # services, agents — orchestrates domain
  infrastructure/  # concrete repos, flows, external clients
  interface/       # FastAPI routers, request/response schemas
```

- **Domain** must not import from infrastructure or interface.
- **Application services** receive repositories via constructor injection; never instantiate repos directly.
- **Interface routers** are thin — delegate all logic to application services. Keep HTTP concerns (status codes, HTTPException) here, not in services.
- When adding a new domain, mirror this structure exactly.

## Type Checking

- Pyright is enforced in CI via pre-commit. All code must pass cleanly.
- When fixing type checking errors, make sure to validate the fix with `uv run pyright`
- Prefer `cast()` over `# type: ignore` when working around third-party stub gaps. Use `# type: ignore` only as a last resort with a comment explaining why.
- Avoid bare `Any`. Use `Any` only when the type is genuinely unknowable (e.g. heterogeneous registries). Document why.
- For SQLAlchemy `where()` clauses, `cast(ColumnElement[bool], ...)` is the established pattern.

## Testing

- Tests use SQLite (`aiosqlite`) with a fresh schema per test — no shared state between tests.
- Use `client` fixture for API-level tests (exercises full FastAPI stack with DB override).
- Use `session` fixture directly for repository/service-level tests.
- External dependencies (Pub/Sub, Storage) are always mocked via `mock_publisher` / `mock_storage` fixtures.
- Prefect flows run in-process via `run_deployment_inline` fixture + `prefect_test_harness`. Use the `@pytest.mark.integration` marker for integration tests (which usually require this).
- **When adding a new flow**, register it in `flows.py` so it can be exercised inline during tests.

## Database & Migrations

- Models live in `domain/models/` as SQLModel classes (`table=True`).
- Always generate migrations with `--autogenerate`; review the generated file before committing.
- Never write raw SQL in application code — use SQLModel/SQLAlchemy constructs.
- Use `model_dump(exclude_unset=True)` for partial updates to avoid overwriting fields with `None`.

## Flows (Prefect)

- Flows are in `infrastructure/flows/`; each domain has its own subpackage.
- Each flow module must export a `FLOW_NAME` constant and register itself in the domain's `flows/__init__.py` `FLOWS` dict.
- Keep `@flow` functions thin — delegate heavy logic to `@task` functions for observability and retries.
- Flows acquire their DB session via `with_session()` (from `core.db`), not via FastAPI dependency injection.

## GCP / External Services

- Never instantiate `storage.Client` or `pubsub_v1.PublisherClient` directly in route handlers — use the `get_storage_client` / `get_publisher` FastAPI dependencies so they can be overridden in tests.
- Pub/Sub topic names are constants defined at the router level, not buried in business logic.
