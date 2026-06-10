from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import httpx


class DataSourceError(RuntimeError):
    pass


class FootballDataSource(ABC):
    name: str

    def __init__(self, timeout: float = 20.0) -> None:
        self.timeout = timeout

    def get_json(self, url: str, headers: dict[str, str] | None = None) -> Any:
        try:
            response = httpx.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as exc:
            raise DataSourceError(f"{self.name} request failed for {url}: {exc}") from exc
        except ValueError as exc:
            raise DataSourceError(f"{self.name} returned invalid JSON for {url}") from exc

    @abstractmethod
    def fetch(self) -> dict[str, Any]:
        """Fetch raw source data."""
