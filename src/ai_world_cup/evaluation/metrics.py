from __future__ import annotations

from dataclasses import dataclass

from ai_world_cup.schemas import Match, Prediction


@dataclass(frozen=True)
class ScoreBreakdown:
    exact_score_points: int
    outcome_points: int
    winner_points: int
    goal_diff_points: int

    @property
    def total_points(self) -> int:
        return (
            self.exact_score_points
            + self.outcome_points
            + self.winner_points
            + self.goal_diff_points
        )


def outcome_for(home_goals: int, away_goals: int) -> str:
    if home_goals > away_goals:
        return "HOME_WIN"
    if home_goals < away_goals:
        return "AWAY_WIN"
    return "DRAW"


def winner_for(match: Match, home_goals: int, away_goals: int) -> str:
    outcome = outcome_for(home_goals, away_goals)
    if outcome == "HOME_WIN":
        return match.home_team_name
    if outcome == "AWAY_WIN":
        return match.away_team_name
    return "DRAW"


def score_prediction(prediction: Prediction, match: Match) -> ScoreBreakdown:
    if match.home_score is None or match.away_score is None:
        raise ValueError("Cannot evaluate match without final score")
    if prediction.home_goals_pred is None or prediction.away_goals_pred is None:
        raise ValueError("Cannot evaluate prediction without predicted score")
    exact = (
        prediction.home_goals_pred == match.home_score
        and prediction.away_goals_pred == match.away_score
    )
    actual_outcome = outcome_for(match.home_score, match.away_score)
    predicted_outcome = prediction.outcome_pred
    actual_winner = winner_for(match, match.home_score, match.away_score)
    predicted_goal_diff = prediction.home_goals_pred - prediction.away_goals_pred
    actual_goal_diff = match.home_score - match.away_score
    return ScoreBreakdown(
        exact_score_points=5 if exact else 0,
        outcome_points=3 if predicted_outcome == actual_outcome else 0,
        winner_points=(
            2
            if actual_outcome != "DRAW" and prediction.winner_team_name_pred == actual_winner
            else 0
        ),
        goal_diff_points=1 if predicted_goal_diff == actual_goal_diff else 0,
    )
