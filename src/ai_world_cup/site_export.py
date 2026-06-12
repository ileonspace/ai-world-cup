from __future__ import annotations

import json
import re
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

TEAM_ALIASES = {
    "Bosnia & Herzegovina": "Bosnia and Herzegovina",
    "USA": "United States",
    "U.S.A.": "United States",
    "United States of America": "United States",
    "DR Congo": "Democratic Republic of the Congo",
    "Congo DR": "Democratic Republic of the Congo",
    "Ivory Coast": "Ivory Coast",
    "Côte d'Ivoire": "Ivory Coast",
    "Cote d'Ivoire": "Ivory Coast",
    "Türkiye": "Turkey",
    "Curacao": "Curaçao",
}


def _canonical_team_name(name: str | None) -> str:
    if not name:
        return ""
    normalized = " ".join(name.strip().split())
    return TEAM_ALIASES.get(normalized, normalized)


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


def _latest_valid_tournament_responses(
    session: Session,
) -> dict[int, TournamentManualResponse]:
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
    return latest_by_model


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
            team_name = _canonical_team_name(team.name)
            if team_name not in official[group]:
                official[group].append(team_name)
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
                "team": _canonical_team_name(standing.team),
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
                "team": _canonical_team_name(team.name) if team else None,
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
                "home_team": _canonical_team_name(prediction.home_team),
                "away_team": _canonical_team_name(prediction.away_team),
                "predicted_winner": _canonical_team_name(prediction.predicted_winner),
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
                "champion": _canonical_team_name(ranking.champion),
                "runner_up": _canonical_team_name(ranking.runner_up),
                "third_place": _canonical_team_name(ranking.third_place),
                "fourth_place": _canonical_team_name(ranking.fourth_place),
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


def _team_index(session: Session) -> dict[str, dict[str, Any]]:
    teams = {}
    for team in session.exec(select(Team)):
        canonical_name = _canonical_team_name(team.name)
        group = team.group_name.replace("Group ", "") if team.group_name else None
        existing = teams.get(canonical_name, {})
        teams[canonical_name] = {
            "name": canonical_name,
            "fifa_code": existing.get("fifa_code") or team.fifa_code,
            "country": existing.get("country") or team.country or canonical_name,
            "group": existing.get("group") or group,
        }
    return teams


def _empty_group_row(team_name: str, team_meta: dict[str, dict[str, Any]]) -> dict[str, Any]:
    meta = team_meta.get(team_name, {})
    return {
        "team": team_name,
        "fifa_code": meta.get("fifa_code"),
        "country": meta.get("country"),
        "matches_played": 0,
        "wins": 0,
        "draws": 0,
        "losses": 0,
        "goals_for": 0,
        "goals_against": 0,
        "goal_difference": 0,
        "points": 0,
        "rank": 0,
    }


def _apply_group_result(
    rows: dict[str, dict[str, Any]],
    team_meta: dict[str, dict[str, Any]],
    home_team: str,
    away_team: str,
    home_goals: int,
    away_goals: int,
) -> None:
    home_team = _canonical_team_name(home_team)
    away_team = _canonical_team_name(away_team)
    for team_name in (home_team, away_team):
        if team_name not in rows:
            rows[team_name] = _empty_group_row(team_name, team_meta)

    home = rows[home_team]
    away = rows[away_team]
    home["matches_played"] += 1
    away["matches_played"] += 1
    home["goals_for"] += home_goals
    home["goals_against"] += away_goals
    away["goals_for"] += away_goals
    away["goals_against"] += home_goals
    if home_goals > away_goals:
        home["wins"] += 1
        home["points"] += 3
        away["losses"] += 1
    elif home_goals < away_goals:
        away["wins"] += 1
        away["points"] += 3
        home["losses"] += 1
    else:
        home["draws"] += 1
        away["draws"] += 1
        home["points"] += 1
        away["points"] += 1


def _rank_group_rows(rows: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    ranked = []
    for row in rows.values():
        row["goal_difference"] = row["goals_for"] - row["goals_against"]
        ranked.append(row)
    ranked.sort(
        key=lambda row: (
            -row["points"],
            -row["goal_difference"],
            -row["goals_for"],
            row["team"],
        )
    )
    for index, row in enumerate(ranked, start=1):
        row["rank"] = index
    return ranked


def _initial_group_rows(
    team_meta: dict[str, dict[str, Any]],
) -> dict[str, dict[str, dict[str, Any]]]:
    groups: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for team_name, meta in team_meta.items():
        group = meta.get("group")
        if group:
            groups[group][team_name] = _empty_group_row(team_name, team_meta)
    return groups


def _group_tables_from_matches(
    grouped_rows: dict[str, dict[str, dict[str, Any]]],
) -> list[dict[str, Any]]:
    return [
        {"group": group, "rows": _rank_group_rows(rows)}
        for group, rows in sorted(grouped_rows.items())
    ]


def _actual_tournament_view(
    session: Session,
    team_meta: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    groups = _initial_group_rows(team_meta)
    knockout_matches = []
    for match in session.exec(select(Match).order_by(Match.match_number, Match.id)):
        group = match.group_name.replace("Group ", "") if match.group_name else None
        if group and match.home_score is not None and match.away_score is not None:
            groups.setdefault(group, {})
            _apply_group_result(
                groups[group],
                team_meta,
                match.home_team_name,
                match.away_team_name,
                match.home_score,
                match.away_score,
            )
        elif not group:
            knockout_matches.append(
                {
                    "match_number": match.match_number,
                    "stage": match.stage or "Knockout",
                    "home_team": _canonical_team_name(match.home_team_name),
                    "away_team": _canonical_team_name(match.away_team_name),
                    "home_score": match.home_score,
                    "away_score": match.away_score,
                    "winner": None,
                }
            )
    return {
        "source": {
            "id": "actual",
            "label": "Real Results",
            "provider": "Official",
            "kind": "actual",
        },
        "group_tables": _group_tables_from_matches(groups),
        "knockout_rounds": _rounds_from_matches(knockout_matches),
        "final_ranking": None,
        "awards": None,
    }


def _seed_team(seed: str, group_tables: list[dict[str, Any]]) -> str | None:
    compact = seed.strip().upper().replace(" ", "")
    group_by_name = {table["group"].upper(): table["rows"] for table in group_tables}
    direct = re.fullmatch(r"([12])([A-L])", compact)
    if direct:
        rank = int(direct.group(1))
        rows = group_by_name.get(direct.group(2), [])
        if len(rows) >= rank:
            return rows[rank - 1]["team"]

    third_place = re.fullmatch(r"3([A-L](?:/[A-L])*)", compact)
    if third_place:
        candidates = []
        for group in third_place.group(1).split("/"):
            rows = group_by_name.get(group, [])
            if len(rows) >= 3:
                row = rows[2]
                candidates.append(
                    (
                        row["points"],
                        row["goal_difference"],
                        row["goals_for"],
                        row["team"],
                    )
                )
        if candidates:
            return sorted(candidates, reverse=True)[0][3]
    return None


def _resolve_team_reference(name: str, group_tables: list[dict[str, Any]]) -> str:
    canonical = _canonical_team_name(name)
    return _seed_team(canonical, group_tables) or canonical


def _resolve_knockout_match(
    match: dict[str, Any],
    group_tables: list[dict[str, Any]],
) -> dict[str, Any]:
    home_team = _resolve_team_reference(match["home_team"], group_tables)
    away_team = _resolve_team_reference(match["away_team"], group_tables)
    winner = _resolve_team_reference(match["winner"], group_tables) if match.get("winner") else None
    if winner not in {home_team, away_team}:
        if match.get("home_score") is not None and match.get("away_score") is not None:
            winner = home_team if match["home_score"] > match["away_score"] else away_team
    return {
        **match,
        "home_team": home_team,
        "away_team": away_team,
        "winner": winner,
    }


def _rounds_from_matches(matches: list[dict[str, Any]]) -> list[dict[str, Any]]:
    round_order = {
        "Round of 32": 1,
        "Round of 16": 2,
        "Quarter-finals": 3,
        "Quarterfinals": 3,
        "Quarter-final": 3,
        "Semi-finals": 4,
        "Semifinals": 4,
        "Semi-final": 4,
        "Third-place play-off": 5,
        "Third Place": 5,
        "Final": 6,
    }
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for match in matches:
        grouped[match["stage"] or "Knockout"].append(match)
    return [
        {
            "stage": stage,
            "matches": sorted(
                stage_matches,
                key=lambda match: match.get("match_number") or 999,
            ),
        }
        for stage, stage_matches in sorted(
            grouped.items(),
            key=lambda item: (round_order.get(item[0], 99), item[0]),
        )
    ]


def _model_tournament_view(
    response: TournamentManualResponse,
    model: LLMModel | None,
    predictions: list[TournamentPrediction],
    final_ranking: PredictedFinalRanking | None,
    team_meta: dict[str, dict[str, Any]],
    awards: PredictedAward | None,
) -> dict[str, Any]:
    groups = _initial_group_rows(team_meta)
    knockout_matches = []
    for prediction in predictions:
        group = prediction.group_name.replace("Group ", "") if prediction.group_name else None
        if prediction.is_official_fixture and group:
            groups.setdefault(group, {})
            _apply_group_result(
                groups[group],
                team_meta,
                prediction.home_team,
                prediction.away_team,
                prediction.predicted_home_goals,
                prediction.predicted_away_goals,
            )
        elif not prediction.is_official_fixture:
            knockout_matches.append(
                {
                    "match_number": prediction.match_number,
                    "stage": prediction.stage,
                    "home_team": _canonical_team_name(prediction.home_team),
                    "away_team": _canonical_team_name(prediction.away_team),
                    "home_score": prediction.predicted_home_goals,
                    "away_score": prediction.predicted_away_goals,
                    "winner": _canonical_team_name(prediction.predicted_winner),
                }
            )
    group_tables = _group_tables_from_matches(groups)
    knockout_matches = [_resolve_knockout_match(match, group_tables) for match in knockout_matches]
    return {
        "source": {
            "id": f"model-{response.model_id}",
            "label": model.model_display_name if model else str(response.model_id),
            "provider": model.provider if model else "",
            "kind": "model",
        },
        "group_tables": group_tables,
        "knockout_rounds": _rounds_from_matches(knockout_matches),
        "final_ranking": {
            "champion": _canonical_team_name(final_ranking.champion),
            "runner_up": _canonical_team_name(final_ranking.runner_up),
            "third_place": _canonical_team_name(final_ranking.third_place),
            "fourth_place": _canonical_team_name(final_ranking.fourth_place),
        }
        if final_ranking
        else None,
        "awards": {
            "top_scorer": awards.top_scorer,
            "best_player": awards.best_player,
            "best_young_player": awards.best_young_player,
            "best_goalkeeper": awards.best_goalkeeper,
        }
        if awards
        else None,
    }


def _tournament_views_payload(session: Session) -> dict[str, Any]:
    team_meta = _team_index(session)
    models = _model_by_id(session)
    latest_responses = _latest_valid_tournament_responses(session)
    response_ids = {response.id for response in latest_responses.values() if response.id}
    predictions_by_response: dict[int, list[TournamentPrediction]] = defaultdict(list)
    for prediction in session.exec(
        select(TournamentPrediction).order_by(
            TournamentPrediction.tournament_manual_response_id,
            TournamentPrediction.match_number,
        )
    ):
        if prediction.tournament_manual_response_id in response_ids:
            predictions_by_response[prediction.tournament_manual_response_id].append(prediction)

    rankings_by_response = {
        ranking.tournament_manual_response_id: ranking
        for ranking in session.exec(select(PredictedFinalRanking))
        if ranking.tournament_manual_response_id in response_ids
    }
    awards_by_response = {
        award.tournament_manual_response_id: award
        for award in session.exec(select(PredictedAward))
        if award.tournament_manual_response_id in response_ids
    }
    views = [_actual_tournament_view(session, team_meta)]
    for response in sorted(
        latest_responses.values(),
        key=lambda item: (
            models.get(item.model_id).model_display_name
            if models.get(item.model_id)
            else str(item.model_id)
        ),
    ):
        if response.id is None:
            continue
        views.append(
            _model_tournament_view(
                response,
                models.get(response.model_id),
                predictions_by_response.get(response.id, []),
                rankings_by_response.get(response.id),
                team_meta,
                awards_by_response.get(response.id),
            )
        )
    return {
        "sources": [view["source"] for view in views],
        "views": views,
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
    tournament_views = _tournament_views_payload(session)
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
        "tournament_views.json": tournament_views,
        "snapshots.json": snapshots,
    }
    written = []
    for filename, payload in files.items():
        path = output_dir / filename
        _dump(path, payload)
        written.append(path)
    return written
