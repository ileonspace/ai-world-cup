from __future__ import annotations

import json
from pathlib import Path

from ai_world_cup.responses.tournament_validator import validate_tournament_response_data
from ai_world_cup.schemas import Match

FIXTURES = Path(__file__).parent / "fixtures"


def test_validate_tournament_response_valid(session) -> None:
    session.add(
        Match(
            match_number=1,
            stage="Group Stage",
            group_name="A",
            home_team_name="Mexico",
            away_team_name="South Africa",
        )
    )
    session.commit()
    data = json.loads((FIXTURES / "sample_tournament_response_valid.json").read_text())
    response, errors, warnings = validate_tournament_response_data(data, session)
    assert response is not None
    assert errors == []
    assert warnings == []


def test_validate_tournament_response_rejects_knockout_draw_winner(session) -> None:
    session.add(
        Match(
            match_number=1,
            stage="Group Stage",
            group_name="A",
            home_team_name="Mexico",
            away_team_name="South Africa",
        )
    )
    session.commit()
    data = json.loads((FIXTURES / "sample_tournament_response_valid.json").read_text())
    data["knockout_predictions"][0]["predicted_home_goals"] = 1
    data["knockout_predictions"][0]["predicted_away_goals"] = 1
    data["knockout_predictions"][0]["predicted_outcome"] = "DRAW"
    data["knockout_predictions"][0]["predicted_winner"] = "DRAW"
    response, errors, _ = validate_tournament_response_data(data, session)
    assert response is None
    assert any("Knockout predictions cannot have DRAW as the winner" in error for error in errors)
