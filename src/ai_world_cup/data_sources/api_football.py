from __future__ import annotations

from typing import Any

from ai_world_cup.config import get_settings
from ai_world_cup.data_sources.base import FootballDataSource


class APIFootballSource(FootballDataSource):
    name = "api_football"
    base_url = "https://v3.football.api-sports.io"

    def __init__(self, season: int = 2026, key: str | None = None) -> None:
        super().__init__()
        self.season = season
        self.key = key if key is not None else get_settings().api_football_key

    @property
    def enabled(self) -> bool:
        return bool(self.key)

    def fetch(self) -> dict[str, Any]:
        if not self.enabled:
            return {"payload": {}, "skipped": "API_FOOTBALL_KEY is not set"}
        headers = {"x-apisports-key": self.key}
        query = f"league=1&season={self.season}"
        return {
            "season": self.season,
            "payload": {
                "fixtures": self.get_json(f"{self.base_url}/fixtures?{query}", headers=headers),
                "teams": self.get_json(f"{self.base_url}/teams?{query}", headers=headers),
                "standings": self.get_json(f"{self.base_url}/standings?{query}", headers=headers),
                "rounds": self.get_json(
                    f"{self.base_url}/fixtures/rounds?{query}", headers=headers
                ),
            },
        }
