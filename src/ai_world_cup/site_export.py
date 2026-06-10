from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from sqlmodel import Session, select

from ai_world_cup.config import get_settings
from ai_world_cup.evaluation.metrics import outcome_for
from ai_world_cup.evaluation.tournament import build_tournament_leaderboard
from ai_world_cup.schemas import (
    DataSnapshot,
    LLMModel,
    Match,
    PredictedAward,
    PredictedFinalRanking,
    PredictedGroupStanding,
    Standing,
    Team,
    TournamentManualResponse,
    TournamentPrediction,
    TournamentPromptRun,
)


def _dump(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")


def _latest_prompt(session: Session) -> TournamentPromptRun | None:
    return session.exec(select(TournamentPromptRun).order_by(TournamentPromptRun.id.desc())).first()


def _latest_snapshot(session: Session) -> DataSnapshot | None:
    return session.exec(select(DataSnapshot).order_by(DataSnapshot.id.desc())).first()


def _model_by_id(session: Session) -> dict[int, LLMModel]:
    return {model.id: model for model in session.exec(select(LLMModel)) if model.id is not None}


def _actual_match_by_number(session: Session) -> dict[int, Match]:
    return {
        match.match_number: match
        for match in session.exec(select(Match))
        if match.match_number is not None
    }


def _prediction_points(prediction: TournamentPrediction, match: Match | None) -> int | None:
    if not match or match.home_score is None or match.away_score is None:
        return None
    points = 0
    exact = (
        prediction.predicted_home_goals == match.home_score
        and prediction.predicted_away_goals == match.away_score
    )
    actual_outcome = outcome_for(match.home_score, match.away_score)
    actual_goal_diff = match.home_score - match.away_score
    predicted_goal_diff = prediction.predicted_home_goals - prediction.predicted_away_goals
    if exact:
        points += 5
    if prediction.predicted_outcome == actual_outcome:
        points += 3
    if actual_outcome != "DRAW":
        actual_winner = (
            match.home_team_name if actual_outcome == "HOME_WIN" else match.away_team_name
        )
        if prediction.predicted_winner == actual_winner:
            points += 2
    if predicted_goal_diff == actual_goal_diff:
        points += 1
    return points


def _models_payload(session: Session) -> list[dict[str, Any]]:
    responses = list(session.exec(select(TournamentManualResponse)))
    latest_response_by_model: dict[int, TournamentManualResponse] = {}
    for response in responses:
        current = latest_response_by_model.get(response.model_id)
        if current is None or response.imported_at > current.imported_at:
            latest_response_by_model[response.model_id] = response
    models = []
    for model in session.exec(
        select(LLMModel).order_by(LLMModel.provider, LLMModel.model_display_name)
    ):
        latest_response = latest_response_by_model.get(model.id or -1)
        models.append(
            {
                "id": model.id,
                "model_display_name": model.model_display_name,
                "provider": model.provider,
                "access_mode": model.access_mode,
                "web_search_enabled": None,
                "submitted_at": latest_response.imported_at.isoformat()
                if latest_response
                else None,
                "notes": model.notes,
            }
        )
    return models


def _fixtures_payload(session: Session) -> list[dict[str, Any]]:
    return [
        {
            "match_number": match.match_number,
            "stage": match.stage,
            "group": match.group_name,
            "home_team": match.home_team_name,
            "away_team": match.away_team_name,
            "kickoff_time": match.kickoff_utc.isoformat() if match.kickoff_utc else None,
            "venue": match.venue_name,
            "status": match.status,
            "home_score": match.home_score,
            "away_score": match.away_score,
            "winner": None,
        }
        for match in session.exec(select(Match).order_by(Match.match_number, Match.id))
    ]


def _leaderboard_payload(session: Session) -> list[dict[str, Any]]:
    rows = build_tournament_leaderboard(session)
    return [
        {
            "rank": index,
            "model_name": row.model_name,
            "provider": row.provider,
            "total_points": row.total_tournament_points,
            "group_stage_points": row.group_stage_points,
            "group_standing_points": row.group_standing_points,
            "knockout_points": row.knockout_points,
            "exact_score_accuracy": row.exact_score_accuracy,
            "outcome_accuracy": row.outcome_accuracy,
            "average_confidence": row.average_confidence,
            "champion_prediction": row.champion_prediction,
        }
        for index, row in enumerate(rows, start=1)
    ]


def _predictions_payload(session: Session) -> list[dict[str, Any]]:
    models = _model_by_id(session)
    actual = _actual_match_by_number(session)
    rows = []
    for prediction in session.exec(
        select(TournamentPrediction).order_by(
            TournamentPrediction.match_number, TournamentPrediction.model_id
        )
    ):
        model = models.get(prediction.model_id)
        match = actual.get(prediction.match_number or -1)
        rows.append(
            {
                "model_name": model.model_display_name if model else str(prediction.model_id),
                "provider": model.provider if model else "",
                "match_number": prediction.match_number,
                "stage": prediction.stage,
                "home_team": prediction.home_team,
                "away_team": prediction.away_team,
                "predicted_home_goals": prediction.predicted_home_goals,
                "predicted_away_goals": prediction.predicted_away_goals,
                "predicted_outcome": prediction.predicted_outcome,
                "predicted_winner": prediction.predicted_winner,
                "confidence": prediction.confidence,
                "reasoning_short": prediction.reasoning_short,
                "points": _prediction_points(prediction, match),
            }
        )
    return rows


def _groups_payload(session: Session) -> dict[str, Any]:
    teams_by_id = {team.id: team for team in session.exec(select(Team)) if team.id is not None}
    official: dict[str, list[str]] = defaultdict(list)
    for team in teams_by_id.values():
        if team.group_name:
            group = team.group_name.replace("Group ", "")
            if team.name not in official[group]:
                official[group].append(team.name)
    predicted = []
    models = _model_by_id(session)
    for standing in session.exec(
        select(PredictedGroupStanding).order_by(
            PredictedGroupStanding.group_name, PredictedGroupStanding.rank
        )
    ):
        model = models.get(standing.model_id)
        predicted.append(
            {
                "model_name": model.model_display_name if model else str(standing.model_id),
                "provider": model.provider if model else "",
                "group": standing.group_name,
                "rank": standing.rank,
                "team": standing.team,
                "points": standing.points,
                "goals_for": standing.goals_for,
                "goals_against": standing.goals_against,
                "goal_difference": standing.goal_difference,
            }
        )
    actual = []
    for standing in session.exec(select(Standing).order_by(Standing.group_name, Standing.rank)):
        team = teams_by_id.get(standing.team_id or -1)
        actual.append(
            {
                "group": standing.group_name,
                "rank": standing.rank,
                "team": team.name if team else None,
                "points": standing.points,
                "goals_for": standing.goals_for,
                "goals_against": standing.goals_against,
                "goal_difference": standing.goal_difference,
            }
        )
    return {
        "official_groups": [
            {"group": group, "teams": sorted(teams)} for group, teams in sorted(official.items())
        ],
        "predicted_group_standings": predicted,
        "actual_standings": actual,
    }


def _knockout_payload(session: Session) -> dict[str, Any]:
    models = _model_by_id(session)
    knockout = []
    champion_counter: Counter[str] = Counter()
    for prediction in session.exec(
        select(TournamentPrediction)
        .where(TournamentPrediction.is_official_fixture == False)  # noqa: E712
        .order_by(TournamentPrediction.model_id, TournamentPrediction.match_number)
    ):
        model = models.get(prediction.model_id)
        knockout.append(
            {
                "model_name": model.model_display_name if model else str(prediction.model_id),
                "provider": model.provider if model else "",
                "match_number": prediction.match_number,
                "stage": prediction.stage,
                "home_team": prediction.home_team,
                "away_team": prediction.away_team,
                "predicted_winner": prediction.predicted_winner,
                "confidence": prediction.confidence,
            }
        )
    final_rankings = []
    for ranking in session.exec(
        select(PredictedFinalRanking).order_by(PredictedFinalRanking.model_id)
    ):
        model = models.get(ranking.model_id)
        champion_counter[ranking.champion] += 1
        final_rankings.append(
            {
                "model_name": model.model_display_name if model else str(ranking.model_id),
                "provider": model.provider if model else "",
                "champion": ranking.champion,
                "runner_up": ranking.runner_up,
                "third_place": ranking.third_place,
                "fourth_place": ranking.fourth_place,
            }
        )
    awards = []
    for award in session.exec(select(PredictedAward).order_by(PredictedAward.model_id)):
        model = models.get(award.model_id)
        awards.append(
            {
                "model_name": model.model_display_name if model else str(award.model_id),
                "provider": model.provider if model else "",
                "top_scorer": award.top_scorer,
                "best_player": award.best_player,
                "best_young_player": award.best_young_player,
                "best_goalkeeper": award.best_goalkeeper,
            }
        )
    return {
        "predicted_knockout_brackets": knockout,
        "final_ranking_predictions": final_rankings,
        "champion_predictions": [
            {"team": team, "count": count} for team, count in champion_counter.most_common()
        ],
        "awards_predictions": awards,
    }


def _snapshots_payload(
    session: Session, prompt: TournamentPromptRun | None
) -> list[dict[str, Any]]:
    return [
        {
            "data_snapshot_id": snapshot.id,
            "source_name": snapshot.source_name,
            "created_at": snapshot.created_at.isoformat(),
            "raw_file_path": snapshot.raw_file_path,
            "prompt_version": prompt.prompt_version if prompt else None,
        }
        for snapshot in session.exec(select(DataSnapshot).order_by(DataSnapshot.id.desc()))
    ]


def export_site_data(session: Session, output_dir: Path | None = None) -> list[Path]:
    output_dir = output_dir or get_settings().resolve_path("website/public/data")
    prompt = _latest_prompt(session)
    snapshot = _latest_snapshot(session)
    leaderboard = _leaderboard_payload(session)
    models = _models_payload(session)
    fixtures = _fixtures_payload(session)
    predictions = _predictions_payload(session)
    groups = _groups_payload(session)
    knockout = _knockout_payload(session)
    snapshots = _snapshots_payload(session, prompt)
    project_summary = {
        "project_name": "AI World Cup",
        "description": (
            "A reproducible benchmark for comparing LLM predictions on FIFA World Cup 2026."
        ),
        "latest_data_snapshot_id": snapshot.id if snapshot else None,
        "prompt_version": prompt.prompt_version if prompt else "v1",
        "number_of_models": len(models),
        "number_of_predictions": len(predictions),
        "number_of_fixtures": len(fixtures),
        "last_updated": datetime.now(UTC).isoformat(),
    }
    files = {
        "project_summary.json": project_summary,
        "leaderboard.json": leaderboard,
        "models.json": models,
        "fixtures.json": fixtures,
        "predictions.json": predictions,
        "groups.json": groups,
        "knockout.json": knockout,
        "snapshots.json": snapshots,
    }
    written = []
    for filename, payload in files.items():
        path = output_dir / filename
        _dump(path, payload)
        written.append(path)
    return written
