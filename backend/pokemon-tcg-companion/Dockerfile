# Stage 1: Builder - Install dependencies and build the application
FROM python:3.12-slim AS builder

WORKDIR /app
RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./
RUN uv sync

# Stage 2: Runtime - Create final, slim image
FROM python:3.12-slim AS runtime
WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY . /app

ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
