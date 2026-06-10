from __future__ import annotations

from ai_world_cup.data_sources.openfootball import OpenFootballSource
from ai_world_cup.data_sources.worldcup26 import WorldCup26Source


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self):
        return self.payload


def test_openfootball_source_mocked(monkeypatch) -> None:
    def fake_get(url, headers=None, timeout=None):
        assert "2026/worldcup.json" in url
        return FakeResponse({"rounds": []})

    monkeypatch.setattr("httpx.get", fake_get)
    data = OpenFootballSource().fetch()
    assert data["payload"] == {"rounds": []}


def test_worldcup26_source_mocked(monkeypatch) -> None:
    def fake_get(url, headers=None, timeout=None):
        return FakeResponse([])

    monkeypatch.setattr("httpx.get", fake_get)
    data = WorldCup26Source().fetch()
    assert set(data["payload"]) == {"games", "groups", "teams", "stadiums"}
