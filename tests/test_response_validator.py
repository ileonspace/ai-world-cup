from __future__ import annotations

import pytest

from ai_world_cup.responses.validator import validate_match_response
from ai_world_cup.schemas import Match


def test_validate_valid_response_matches_prompt() -> None:
    match = Match(home_team_name="Mexico", away_team_name="South Africa")
    response = validate_match_response(
        {
            "home_team": "Mexico",
            "away_team": "South Africa",
            "predicted_home_goals": 2,
            "predicted_away_goals": 1,
            "predicted_outcome": "HOME_WIN",
            "predicted_winner": "Mexico",
            "confidence": 0.8,
            "reasoning_short": "Mexico have home advantage.",
        },
        match,
    )
    assert response.predicted_winner == "Mexico"


def test_validate_invalid_score_outcome_mismatch() -> None:
    match = Match(home_team_name="Mexico", away_team_name="South Africa")
    with pytest.raises(ValueError, match="predicted_outcome"):
        validate_match_response(
            {
                "home_team": "Mexico",
                "away_team": "South Africa",
                "predicted_home_goals": 2,
                "predicted_away_goals": 1,
                "predicted_outcome": "DRAW",
                "predicted_winner": "DRAW",
                "confidence": 0.8,
                "reasoning_short": "Mismatch.",
            },
            match,
        )
