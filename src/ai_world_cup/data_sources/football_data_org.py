from __future__ import annotations

from typing import Any

from ai_world_cup.config import get_settings
from ai_world_cup.data_sources.base import FootballDataSource


class FootballDataOrgSource(FootballDataSource):
    name = "football_data_org"
    base_url = "https://api.football-data.org/v4"

    def __init__(self, season: int = 2026, token: str | None = None) -> None:
        super().__init__()
        self.season = season
        self.token = token if token is not None else get_settings().football_data_token

    @property
    def enabled(self) -> bool:
        return bool(self.token)

    def fetch(self) -> dict[str, Any]:
        if not self.enabled:
            return {"payload": {}, "skipped": "FOOTBALL_DATA_TOKEN is not set"}
        headers = {"X-Auth-Token": self.token}
        return {
            "season": self.season,
            "payload": {
                "matches": self.get_json(
                    f"{self.base_url}/competitions/WC/matches?season={self.season}",
                    headers=headers,
                ),
                "standings": self.get_json(
                    f"{self.base_url}/competitions/WC/standings?season={self.season}",
                    headers=headers,
                ),
            },
        }
