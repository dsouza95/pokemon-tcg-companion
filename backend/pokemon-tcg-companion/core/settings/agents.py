from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    default_agent_model: str = "google-gla:gemini-3-flash-preview"


settings = Settings()  # type: ignore[call-arg] Pydantic fills the values in runtime
