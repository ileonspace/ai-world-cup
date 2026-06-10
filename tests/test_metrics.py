from __future__ import annotations

from ai_world_cup.evaluation.metrics import score_prediction
from ai_world_cup.schemas import Match, Prediction


def test_score_prediction_exact_home_win() -> None:
    match = Match(
        home_team_name="Mexico", away_team_name="South Africa", home_score=2, away_score=1
    )
    prediction = Prediction(
        manual_response_id=1,
        model_id=1,
        match_id=1,
        home_goals_pred=2,
        away_goals_pred=1,
        outcome_pred="HOME_WIN",
        winner_team_name_pred="Mexico",
        parse_status="VALID",
    )
    score = score_prediction(prediction, match)
    assert score.exact_score_points == 5
    assert score.outcome_points == 3
    assert score.winner_points == 2
    assert score.goal_diff_points == 1
    assert score.total_points == 11


def test_draw_has_no_extra_winner_points() -> None:
    match = Match(
        home_team_name="Mexico", away_team_name="South Africa", home_score=1, away_score=1
    )
    prediction = Prediction(
        manual_response_id=1,
        model_id=1,
        match_id=1,
        home_goals_pred=1,
        away_goals_pred=1,
        outcome_pred="DRAW",
        winner_team_name_pred="DRAW",
        parse_status="VALID",
    )
    assert score_prediction(prediction, match).winner_points == 0
