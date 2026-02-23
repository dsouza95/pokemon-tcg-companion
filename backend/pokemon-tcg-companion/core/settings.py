from __future__ import annotations

from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    allowed_origins: str = ""
    clerk_secret_key: str = ""
    clerk_authorized_party: str = "http://localhost:3000"
    database_url: str = "sqlite+aiosqlite:///./test.db"
    default_agent_model: str = "google-gla:gemini-2.5-flash"
    default_flow_retries: int = 3
    default_flow_retry_delay_seconds: int = 10
    gcp_bucket: Optional[str] = None
    gcp_pubsub_project: str = "local-project"
    google_application_credentials_json: Optional[str] = None
    prefect_deployment: str = "default"
    log_level: str = "INFO"


settings = Settings()
