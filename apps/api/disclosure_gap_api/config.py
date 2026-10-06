from __future__ import annotations

from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "local-synthetic"
    database_url: str = "sqlite:///./disclosure-gap.sqlite"
    allow_real_participant_data: bool = False
    real_data_readiness_approved: bool = False
    consent_version: str = "0.2.0"
    enforce_study_windows: bool = True
    web_origin: str = "http://localhost:3000"

    @model_validator(mode="after")
    def enforce_real_data_gate(self) -> Settings:
        if self.allow_real_participant_data and not self.real_data_readiness_approved:
            raise ValueError("ALLOW_REAL_PARTICIPANT_DATA requires REAL_DATA_READINESS_APPROVED")
        if (
            self.app_env in {"local-synthetic", "test", "public-demo"}
            and self.allow_real_participant_data
        ):
            raise ValueError(f"{self.app_env} must remain synthetic-only")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
