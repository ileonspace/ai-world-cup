from __future__ import annotations

from dataclasses import dataclass

from sqlmodel import Session, select

from ai_world_cup.evaluation.metrics import outcome_for
from ai_world_cup.schemas import EvaluationResult, LLMModel, Match, Prediction


@dataclass(frozen=True)
class LeaderboardRow:
    rank: int
    model_name: str
    provider: str
    matches_predicted: int
    total_points: int
    average_points: float
    outcome_accuracy: float
    exact_score_accuracy: float
    average_confidence: float


def build_leaderboard(session: Session) -> list[LeaderboardRow]:
    models = list(session.exec(select(LLMModel)))
    rows: list[LeaderboardRow] = []
    for model in models:
        predictions = list(session.exec(select(Prediction).where(Prediction.model_id == model.id)))
        if not predictions:
            continue
        total_points = 0
        exact_count = 0
        outcome_count = 0
        evaluated_count = 0
        confidences: list[float] = []
        for prediction in predictions:
            if prediction.confidence is not None:
                confidences.append(prediction.confidence)
            match = session.get(Match, prediction.match_id)
            if not match or match.home_score is None or match.away_score is None:
                continue
            result = session.exec(
                select(EvaluationResult).where(
                    EvaluationResult.model_id == model.id,
                    EvaluationResult.match_id == match.id,
                )
            ).first()
            if result:
                total_points += result.total_points
            evaluated_count += 1
            if (
                prediction.home_goals_pred == match.home_score
                and prediction.away_goals_pred == match.away_score
            ):
                exact_count += 1
            if prediction.outcome_pred == outcome_for(match.home_score, match.away_score):
                outcome_count += 1
        denom = evaluated_count or len(predictions)
        rows.append(
            LeaderboardRow(
                rank=0,
                model_name=model.model_display_name,
                provider=model.provider,
                matches_predicted=len(predictions),
                total_points=total_points,
                average_points=total_points / denom if denom else 0.0,
                outcome_accuracy=outcome_count / evaluated_count if evaluated_count else 0.0,
                exact_score_accuracy=exact_count / evaluated_count if evaluated_count else 0.0,
                average_confidence=sum(confidences) / len(confidences) if confidences else 0.0,
            )
        )
    sorted_rows = sorted(
        rows, key=lambda row: (-row.total_points, -row.average_points, row.model_name)
    )
    return [
        LeaderboardRow(rank=index, **{k: v for k, v in row.__dict__.items() if k != "rank"})
        for index, row in enumerate(sorted_rows, start=1)
    ]
