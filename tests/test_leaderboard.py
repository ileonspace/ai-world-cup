from __future__ import annotations

from ai_world_cup.evaluation.leaderboard import build_leaderboard
from ai_world_cup.schemas import EvaluationResult, LLMModel, Match, Prediction


def test_leaderboard_ranking(session) -> None:
    model_a = LLMModel(model_display_name="Model A", provider="Provider")
    model_b = LLMModel(model_display_name="Model B", provider="Provider")
    match = Match(
        home_team_name="Mexico", away_team_name="South Africa", home_score=2, away_score=1
    )
    session.add(model_a)
    session.add(model_b)
    session.add(match)
    session.commit()
    session.refresh(model_a)
    session.refresh(model_b)
    session.refresh(match)
    session.add(
        Prediction(
            manual_response_id=1,
            model_id=model_a.id,
            match_id=match.id,
            home_goals_pred=2,
            away_goals_pred=1,
            outcome_pred="HOME_WIN",
            winner_team_name_pred="Mexico",
            confidence=0.7,
            parse_status="VALID",
        )
    )
    session.add(
        Prediction(
            manual_response_id=2,
            model_id=model_b.id,
            match_id=match.id,
            home_goals_pred=1,
            away_goals_pred=1,
            outcome_pred="DRAW",
            winner_team_name_pred="DRAW",
            confidence=0.6,
            parse_status="VALID",
        )
    )
    session.add(EvaluationResult(model_id=model_a.id, match_id=match.id, total_points=11))
    session.add(EvaluationResult(model_id=model_b.id, match_id=match.id, total_points=0))
    session.commit()
    rows = build_leaderboard(session)
    assert rows[0].model_name == "Model A"
    assert rows[0].rank == 1
    assert rows[0].outcome_accuracy == 1.0
    assert rows[1].rank == 2
