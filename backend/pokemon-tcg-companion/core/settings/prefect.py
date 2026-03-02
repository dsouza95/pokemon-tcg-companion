from __future__ import annotations

from pydantic import SecretStr
from pydantic_settings import BaseSettings


class PrefectSettings(BaseSettings):
    database_url: SecretStr
    default_flow_retries: int = 3
    default_flow_retry_delay_seconds: int = 10
    gcp_bucket: str
    prefect_deployment: str = "default"
    log_level: str = "DEBUG"


settings = PrefectSettings()  # type: ignore[call-arg] Pydantic fills the values in runtime
