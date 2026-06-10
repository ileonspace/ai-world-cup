from __future__ import annotations

import json
from pathlib import Path

from ai_world_cup.data.normalize import normalize_openfootball, normalize_worldcup26

FIXTURES = Path(__file__).parent / "fixtures"


def test_normalize_openfootball() -> None:
    raw = json.loads((FIXTURES / "sample_openfootball_2026.json").read_text())
    teams, matches = normalize_openfootball(raw)
    assert {team.name for team in teams} == {"Mexico", "South Africa"}
    assert len(matches) == 1
    assert matches[0].home_team_name == "Mexico"
    assert matches[0].group_name == "Group A"


def test_normalize_worldcup26() -> None:
    raw = json.loads((FIXTURES / "sample_worldcup26_games.json").read_text())
    teams, stadiums, matches = normalize_worldcup26(raw)
    assert len(teams) == 2
    assert stadiums[0].city == "Mexico City"
    assert matches[0].venue_name == "Estadio Azteca"
