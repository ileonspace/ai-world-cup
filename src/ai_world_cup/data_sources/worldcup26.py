from __future__ import annotations

from typing import Any

from ai_world_cup.data_sources.base import DataSourceError, FootballDataSource


class WorldCup26Source(FootballDataSource):
    name = "worldcup26"
    base_url = "https://worldcup26.ir"
    endpoints = {
        "games": "/get/games",
        "groups": "/get/groups",
        "teams": "/get/teams",
        "stadiums": "/get/stadiums",
    }

    def fetch(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        errors: dict[str, str] = {}
        for key, endpoint in self.endpoints.items():
            url = f"{self.base_url}{endpoint}"
            try:
                result[key] = self.get_json(url)
            except DataSourceError as exc:
                errors[key] = str(exc)
                result[key] = []
        return {"payload": result, "errors": errors}
