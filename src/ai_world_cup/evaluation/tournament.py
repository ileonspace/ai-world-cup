from __future__ import annotations

from dataclasses import dataclass

from sqlmodel import Session, select

from ai_world_cup.evaluation.metrics import outcome_for
from ai_world_cup.schemas import (
    LLMModel,
    Match,
    PredictedFinalRanking,
    PredictedGroupStanding,
    Standing,
    Team,
    TournamentManualResponse,
    TournamentPrediction,
)

GROUP_STAGE_EXACT_SCORE = 5
GROUP_STAGE_OUTCOME = 3
GROUP_STAGE_WINNER = 2
GROUP_STAGE_GOAL_DIFF = 1

ROUND_POINTS = {
    "round of 32": 2,
    "round of 16": 4,
    "quarter": 6,
    "semi": 8,
    "final": 12,
}


@dataclass(frozen=True)
class TournamentScore:
    model_id: int
    model_name: str
    provider: str
    total_tournament_points: int
    group_stage_points: int
    group_standing_points: int
    knockout_points: int
    champion_prediction: str
    exact_score_accuracy: float
    outcome_accuracy: float
    average_confidence: float


def _actual_match_by_number(session: Session) -> dict[int, Match]:
    matches = session.exec(select(Match).where(Match.match_number.is_not(None)))
    return {match.match_number: match for match in matches if match.match_number is not None}


def _score_official_prediction(
    prediction: TournamentPrediction, match: Match
) -> tuple[int, bool, bool]:
    if match.home_score is None or match.away_score is None:
        return 0, False, False
    points = 0
    exact = (
        prediction.predicted_home_goals == match.home_score
        and prediction.predicted_away_goals == match.away_score
    )
    actual_outcome = outcome_for(match.home_score, match.away_score)
    predicted_goal_diff = prediction.predicted_home_goals - prediction.predicted_away_goals
    actual_goal_diff = match.home_score - match.away_score
    if exact:
        points += GROUP_STAGE_EXACT_SCORE
    if prediction.predicted_outcome == actual_outcome:
        points += GROUP_STAGE_OUTCOME
    if actual_outcome != "DRAW" and prediction.predicted_winner in {
        match.home_team_name,
        match.away_team_name,
    }:
        actual_winner = (
            match.home_team_name if actual_outcome == "HOME_WIN" else match.away_team_name
        )
        if prediction.predicted_winner == actual_winner:
            points += GROUP_STAGE_WINNER
    if predicted_goal_diff == actual_goal_diff:
        points += GROUP_STAGE_GOAL_DIFF
    return points, exact, prediction.predicted_outcome == actual_outcome


def _actual_standings(session: Session) -> dict[str, list[Standing]]:
    standings = list(session.exec(select(Standing).order_by(Standing.group_name, Standing.rank)))
    grouped: dict[str, list[Standing]] = {}
    for standing in standings:
        if standing.group_name:
            grouped.setdefault(standing.group_name, []).append(standing)
    return grouped


def _team_name_for_standing(session: Session, standing: Standing) -> str | None:
    if standing.team_id is None:
        return None
    team = session.get(Team, standing.team_id)
    return team.name if team else None


def _score_group_standings(session: Session, response_id: int) -> int:
    # Standing rows do not currently duplicate team names, so this scoring activates when
    # normalized standing team IDs are resolvable through teams in a later data import.
    actual = _actual_standings(session)
    if not actual:
        return 0
    predicted = list(
        session.exec(
            select(PredictedGroupStanding).where(
                PredictedGroupStanding.tournament_manual_response_id == response_id
            )
        )
    )
    points = 0
    for group_name, actual_rows in actual.items():
        actual_names = [
            name
            for row in actual_rows
            if (name := _team_name_for_standing(session, row)) is not None
        ]
        if not actual_names:
            continue
        predicted_rows = sorted(
            [row for row in predicted if row.group_name == group_name], key=lambda row: row.rank
        )
        predicted_names = [row.team for row in predicted_rows]
        if predicted_names[:1] == actual_names[:1]:
            points += 5
        if set(predicted_names[:2]) == set(actual_names[:2]):
            points += 5
        for _team in set(predicted_names[:3]) & set(actual_names[:3]):
            points += 3
        for index, team in enumerate(predicted_names):
            if index < len(actual_names) and actual_names[index] == team:
                points += 2
    return points


def _stage_key(stage: str) -> str:
    normalized = stage.lower()
    if "round of 32" in normalized:
        return "round of 32"
    if "round of 16" in normalized:
        return "round of 16"
    if "quarter" in normalized:
        return "quarter"
    if "semi" in normalized:
        return "semi"
    if normalized.strip() == "final":
        return "final"
    return normalized


def _is_placeholder_team(name: str | None) -> bool:
    if not name:
        return True
    text = name.upper()
    return any(char.isdigit() for char in text) or "/" in text


def _score_knockout(
    predictions: list[TournamentPrediction], actual_matches: dict[int, Match]
) -> int:
    points = 0
    for prediction in predictions:
        stage_key = _stage_key(prediction.stage)
        stage_points = ROUND_POINTS.get(stage_key, 0)
        if stage_points and prediction.match_number in actual_matches:
            match = actual_matches[prediction.match_number]
            if _is_placeholder_team(match.home_team_name) or _is_placeholder_team(
                match.away_team_name
            ):
                continue
            actual_teams = {match.home_team_name, match.away_team_name}
            for team in {prediction.home_team, prediction.away_team} & actual_teams:
                if team:
                    points += stage_points
            if match.home_score is not None and match.away_score is not None:
                actual_outcome = outcome_for(match.home_score, match.away_score)
                actual_winner = (
                    match.home_team_name if actual_outcome == "HOME_WIN" else match.away_team_name
                )
                if actual_outcome != "DRAW" and prediction.predicted_winner == actual_winner:
                    points += stage_points
    return points


def _score_final_ranking(session: Session, response_id: int) -> tuple[int, str]:
    ranking = session.exec(
        select(PredictedFinalRanking).where(
            PredictedFinalRanking.tournament_manual_response_id == response_id
        )
    ).first()
    if not ranking:
        return 0, ""
    points = 0
    # Final actual ranking is not part of the current base schema; champion is scored
    # through knockout final winner when the final fixture/result is available.
    return points, ranking.champion


def score_tournament_response(
    session: Session,
    manual_response: TournamentManualResponse,
    completed_only: bool = True,
) -> TournamentScore:
    model = session.get(LLMModel, manual_response.model_id)
    predictions = list(
        session.exec(
            select(TournamentPrediction).where(
                TournamentPrediction.tournament_manual_response_id == manual_response.id
            )
        )
    )
    actual_by_number = _actual_match_by_number(session)
    group_stage_points = 0
    exact_count = 0
    outcome_count = 0
    evaluated_count = 0
    confidences = [prediction.confidence for prediction in predictions]
    for prediction in predictions:
        if not prediction.is_official_fixture or prediction.match_number not in actual_by_number:
            continue
        match = actual_by_number[prediction.match_number]
        if completed_only and (match.home_score is None or match.away_score is None):
            continue
        points, exact, outcome = _score_official_prediction(prediction, match)
        group_stage_points += points
        evaluated_count += 1
        exact_count += int(exact)
        outcome_count += int(outcome)
    group_standing_points = _score_group_standings(session, manual_response.id)
    knockout_predictions = [
        prediction for prediction in predictions if not prediction.is_official_fixture
    ]
    knockout_points = _score_knockout(knockout_predictions, actual_by_number)
    ranking_points, champion = _score_final_ranking(session, manual_response.id)
    knockout_points += ranking_points
    return TournamentScore(
        model_id=manual_response.model_id,
        model_name=model.model_display_name if model else str(manual_response.model_id),
        provider=model.provider if model else "",
        total_tournament_points=group_stage_points + group_standing_points + knockout_points,
        group_stage_points=group_stage_points,
        group_standing_points=group_standing_points,
        knockout_points=knockout_points,
        champion_prediction=champion,
        exact_score_accuracy=exact_count / evaluated_count if evaluated_count else 0.0,
        outcome_accuracy=outcome_count / evaluated_count if evaluated_count else 0.0,
        average_confidence=sum(confidences) / len(confidences) if confidences else 0.0,
    )


def build_tournament_leaderboard(
    session: Session,
    completed_only: bool = True,
) -> list[TournamentScore]:
    responses = list(
        session.exec(
            select(TournamentManualResponse).where(
                TournamentManualResponse.parse_status != "INVALID"
            )
        )
    )
    latest_by_model: dict[int, TournamentManualResponse] = {}
    for response in responses:
        current = latest_by_model.get(response.model_id)
        if current is None or response.imported_at > current.imported_at:
            latest_by_model[response.model_id] = response
    rows = [
        score_tournament_response(session, response, completed_only)
        for response in latest_by_model.values()
    ]
    return sorted(
        rows,
        key=lambda row: (-row.total_tournament_points, -row.group_stage_points, row.model_name),
    )
