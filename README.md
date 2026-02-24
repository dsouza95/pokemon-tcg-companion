# Pokemon TCG Companion

An AI-powered Pokémon TCG companion. Upload a picture of a card to easily retrieve it's information.

## Architecture

The project is split into two services:

- **Backend** (`backend/`) — Python/FastAPI REST API. Background work (AI agents, feature extraction, etc) runs as Prefect flows triggered via Google Pub/Sub.
- **Frontend** (`webapp/`) — Next.js web app, the user-facing UI.

## Tech Stack

### Backend

| Category | Library |
|---|---|
| Web framework | [FastAPI](https://fastapi.tiangolo.com/) |
| ORM | SQLAlchemy |
| Database | PostgreSQL |
| AI agents | [PydanticAI](https://ai.pydantic.dev/) |
| Background flows | [Prefect](https://www.prefect.io/) |
| Observability | [Logfire](https://logfire.pydantic.dev/) |

### Frontend

| Category | Library |
|---|---|
| Framework | [Next.js](https://nextjs.org/) 16  |
| UI runtime | React 19 |
| Components | [shadcn/ui](https://ui.shadcn.com/) |
| Query | TanStack Query |

## Setup

### Prerequisites

- [uv](https://docs.astral.sh/uv/) — Python package manager
- [pnpm](https://pnpm.io/) — Node package manager
- [Docker](https://www.docker.com/) — for local infrastructure
- A Google Cloud project with Storage and Pub/Sub enabled
- An AI provider (we use Open router by default)



### 1. Infrastructure

Start PostgreSQL, Prefect, and the Pub/Sub emulator:

```bash
cd backend/pokemon-tcg-companion
docker compose up -d
```

### 2. Backend

Copy the environment file and fill in the values:

```bash
cp .envrc.example .envrc
# edit .envrc — see variable descriptions in the file
```

Install dependencies and run migrations:

```bash
uv sync
uv run alembic -c alembic.ini upgrade head
```

Set up the Pub/Sub topic and subscription:

```bash
uv run python scripts/create_topic_sub.py
```

Set CORS on the GCS bucket (required for direct browser uploads):

```bash
uv run python scripts/set_bucket_cors.py
```

#### Logfire (Observability)

The backend ships with [Logfire](https://logfire.pydantic.dev/docs/) instrumentation. To send traces to your own project:

1. Create a free account at <https://logfire.pydantic.dev>.
2. Authenticate the CLI:
   ```bash
   uv run logfire auth
   ```
3. Link a project:
   ```bash
   uv run logfire projects use <your-project-name>
   ```

Without a token the app still starts — traces are simply discarded and a warning is logged. See the [Logfire first-steps guide](https://logfire.pydantic.dev/docs/guides/first-steps/) for more details.

### 3. Frontend

```bash
cd webapp
pnpm install
```

Create a `.env.local` pointing at the backend:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Running Locally

**Backend** — starts both the FastAPI server and the Prefect flow server:

```bash
cd backend/pokemon-tcg-companion
uv run honcho start
```

Or run them separately:

```bash
uv run fastapi dev --port 8000          # API server
uv run python scripts/serve_flows.py    # Prefect flow worker
```

**Frontend:**

```bash
cd webapp
pnpm dev
```

The app is available at `http://localhost:3000`.

## Demo

A demo of the full application (frontend and backend) is available at https://pokemon-tcg-companion-beta.vercel.app/cards. Because the demo is hosted exclusively on free-tier services, it may be slower than a production deployment or temporarily unavailable.

## Development

### Backend

```bash
uv run pytest                                       # tests
uv run pyright                                      # type checking
uv run ruff check --fix .                           # lint
uv run ruff format .                                # format
uv run alembic revision --autogenerate -m "<msg>"   # new migration
uv run python scripts/generate_openapi.py           # regenerate OpenAPI schema
```

### Frontend

```bash
pnpm lint       # ESLint
pnpm build      # production build
pnpm openapi    # regenerate TypeScript types from OpenAPI schema
```

When the backend API schema changes, run `uv run python scripts/generate_openapi.py` in the backend, copy the output to `webapp/lib/openapi.json`, then run `pnpm openapi` in the frontend to update the typed API client.
