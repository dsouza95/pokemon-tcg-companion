from __future__ import annotations

from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    allowed_origins: str = ""
    backend_url: str = "http://localhost:8000"
    database_url: str = "sqlite+aiosqlite:///./test.db"
    default_agent_model: str = "google-gla:gemini-3-flash-preview"
    default_flow_retries: int = 3
    default_flow_retry_delay_seconds: int = 10
    gcp_bucket: Optional[str] = None
    gcp_pubsub_project: str = "local-project"
    prefect_deployment: str = "default"
    log_level: str = "INFO"


settings = Settings()
