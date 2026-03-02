from __future__ import annotations

from pydantic import SecretStr
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    database_url: SecretStr


settings = DatabaseSettings()  # type: ignore[call-arg] Pydantic fills the values in runtime
