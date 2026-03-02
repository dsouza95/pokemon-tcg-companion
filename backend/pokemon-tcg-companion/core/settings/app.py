from __future__ import annotations

from typing import Optional

from pydantic import SecretStr
from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    allowed_origins: str = "http://localhost:3000"
    clerk_secret_key: SecretStr
    clerk_authorized_party: str = "http://localhost:3000"
    database_url: SecretStr
    electric_source_id: str = "my-source-id"
    electric_source_secret: SecretStr = SecretStr("my-source-secret")
    electric_service_url: str = "http://localhost:3001/v1/shape"
    gcp_bucket: str
    gcp_pubsub_project: str = "local-project"
    pubsub_audience: Optional[str] = None
    pubsub_service_account_email: Optional[SecretStr] = None
    google_application_credentials_json: Optional[SecretStr] = None
    log_level: str = "DEBUG"


settings = AppSettings()  # type: ignore[call-arg] Pydantic fills the values in runtime
