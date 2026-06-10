from __future__ import annotations

from typing import Any

from ai_world_cup.data_sources.base import FootballDataSource


class OpenFootballSource(FootballDataSource):
    name = "openfootball"
    base_url = "https://raw.githubusercontent.com/openfootball/worldcup.json/master"

    def __init__(self, season: int = 2026) -> None:
        super().__init__()
        self.season = season

    def fetch(self) -> dict[str, Any]:
        url = f"{self.base_url}/{self.season}/worldcup.json"
        return {"season": self.season, "url": url, "payload": self.get_json(url)}
