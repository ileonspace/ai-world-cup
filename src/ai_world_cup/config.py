from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///data/processed/ai_world_cup.sqlite"
    football_data_token: str = ""
    api_football_key: str = ""
    project_root: Path = Field(default_factory=lambda: Path.cwd())

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    def resolve_path(self, path: str | Path) -> Path:
        candidate = Path(path)
        if candidate.is_absolute():
            return candidate
        return self.project_root / candidate


@lru_cache
def get_settings() -> Settings:
    return Settings()
