from __future__ import annotations

from collections import Counter, defaultdict

from pydantic import ValidationError
from sqlmodel import Session, select

from ai_world_cup.responses.tournament_response_schema import TournamentPredictionResponse
from ai_world_cup.schemas import Match

KEY_ALIASES = {
    "promptversion": "prompt_version",
    "datasnapshotid": "data_snapshot_id",
    "modelname": "model_name",
    "predictioncreatedat": "prediction_created_at",
    "groupstagepredictions": "group_stage_predictions",
    "predictedgroupstandings": "predicted_group_standings",
    "knockoutpredictions": "knockout_predictions",
    "finalranking": "final_ranking",
    "awardspredictions": "awards_predictions",
    "matchnumber": "match_number",
    "hometeam": "home_team",
    "awayteam": "away_team",
    "predictedhomegoals": "predicted_home_goals",
    "predictedawaygoals": "predicted_away_goals",
    "predictedoutcome": "predicted_outcome",
    "predictedwinner": "predicted_winner",
    "reasoningshort": "reasoning_short",
    "goalsfor": "goals_for",
    "goalsagainst": "goals_against",
    "goaldifference": "goal_difference",
    "runnerup": "runner_up",
    "thirdplace": "third_place",
    "fourthplace": "fourth_place",
    "topscorer": "top_scorer",
    "bestplayer": "best_player",
    "bestyoungplayer": "best_young_player",
    "bestgoalkeeper": "best_goalkeeper",
}

VALUE_ALIASES = {
    "HOMEWIN": "HOME_WIN",
    "AWAYWIN": "AWAY_WIN",
    "HOME WIN": "HOME_WIN",
    "AWAY WIN": "AWAY_WIN",
}


def is_group_stage_match(match: Match) -> bool:
    return match.group_name is not None


def official_group_stage_matches(session: Session) -> list[Match]:
    return list(
        session.exec(select(Match).order_by(Match.match_number, Match.kickoff_utc, Match.id))
    )


def _normalize_group(group: str | None) -> str | None:
    if not group:
        return None
    text = group.strip()
    if text.lower().startswith("group "):
        return text.split(maxsplit=1)[1]
    return text


def _match_key(match: Match) -> tuple[int | None, str, str, str | None]:
    return (
        match.match_number,
        match.home_team_name,
        match.away_team_name,
        _normalize_group(match.group_name),
    )


def _prediction_key(match_number: int | None, home: str, away: str, group: str | None):
    return (match_number, home, away, _normalize_group(group))


def normalize_tournament_payload(value):
    if isinstance(value, list):
        return [normalize_tournament_payload(item) for item in value]
    if isinstance(value, dict):
        normalized = {}
        for key, item in value.items():
            clean_key = str(key).replace("_", "").lower()
            normalized[KEY_ALIASES.get(clean_key, key)] = normalize_tournament_payload(item)
        if normalized.get("predicted_outcome") == "DRAW" and normalized.get(
            "predicted_home_goals"
        ) == normalized.get("predicted_away_goals"):
            if normalized.get("predicted_winner") == normalized.get("home_team"):
                normalized["predicted_outcome"] = "HOME_WIN"
            elif normalized.get("predicted_winner") == normalized.get("away_team"):
                normalized["predicted_outcome"] = "AWAY_WIN"
        return normalized
    if isinstance(value, str):
        return VALUE_ALIASES.get(value.strip().upper(), value)
    return value


def _computed_group_tables(
    response: TournamentPredictionResponse,
) -> dict[str, dict[str, dict[str, int]]]:
    tables: dict[str, dict[str, dict[str, int]]] = defaultdict(
        lambda: defaultdict(
            lambda: {
                "points": 0,
                "goals_for": 0,
                "goals_against": 0,
                "goal_difference": 0,
            }
        )
    )
    for pred in response.group_stage_predictions:
        if not pred.group:
            continue
        home = tables[pred.group][pred.home_team]
        away = tables[pred.group][pred.away_team]
        home["goals_for"] += pred.predicted_home_goals
        home["goals_against"] += pred.predicted_away_goals
        away["goals_for"] += pred.predicted_away_goals
        away["goals_against"] += pred.predicted_home_goals
        home["goal_difference"] = home["goals_for"] - home["goals_against"]
        away["goal_difference"] = away["goals_for"] - away["goals_against"]
        if pred.predicted_home_goals > pred.predicted_away_goals:
            home["points"] += 3
        elif pred.predicted_home_goals < pred.predicted_away_goals:
            away["points"] += 3
        else:
            home["points"] += 1
            away["points"] += 1
    return tables


def validate_tournament_response_data(
    data: dict,
    session: Session,
) -> tuple[TournamentPredictionResponse | None, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    data = normalize_tournament_payload(data)
    try:
        response = TournamentPredictionResponse.model_validate(data)
    except ValidationError as exc:
        return (
            None,
            [f"{'.'.join(str(part) for part in err['loc'])}: {err['msg']}" for err in exc.errors()],
            [],
        )

    if response.metadata.project != "AI World Cup":
        errors.append("metadata.project must be AI World Cup")

    official_matches = [
        match for match in official_group_stage_matches(session) if is_group_stage_match(match)
    ]
    official_keys = Counter(_match_key(match) for match in official_matches)
    prediction_keys = Counter(
        _prediction_key(pred.match_number, pred.home_team, pred.away_team, pred.group)
        for pred in response.group_stage_predictions
    )
    if official_keys != prediction_keys:
        missing = list((official_keys - prediction_keys).elements())
        extra = list((prediction_keys - official_keys).elements())
        if missing:
            errors.append(f"Missing official group-stage fixtures: {missing[:5]}")
        if extra:
            errors.append(f"Unexpected or duplicate group-stage fixtures: {extra[:5]}")

    official_by_number = {
        match.match_number: match for match in official_matches if match.match_number is not None
    }
    for pred in response.group_stage_predictions:
        if pred.match_number in official_by_number:
            match = official_by_number[pred.match_number]
            if pred.home_team != match.home_team_name or pred.away_team != match.away_team_name:
                errors.append(
                    f"Match {pred.match_number} teams must be "
                    f"{match.home_team_name} vs {match.away_team_name}"
                )

    computed = _computed_group_tables(response)
    for standing in response.predicted_group_standings:
        table_row = computed.get(standing.group, {}).get(standing.team)
        if table_row and (
            standing.points != table_row["points"]
            or standing.goals_for != table_row["goals_for"]
            or standing.goals_against != table_row["goals_against"]
            or standing.goal_difference != table_row["goal_difference"]
        ):
            warnings.append(
                f"Group standing for {standing.team} in {standing.group} is not score-consistent"
            )

    final = next(
        (pred for pred in response.knockout_predictions if pred.stage.strip().lower() == "final"),
        None,
    )
    if final:
        loser = final.away_team if final.predicted_winner == final.home_team else final.home_team
        if response.final_ranking.champion != final.predicted_winner:
            warnings.append("Champion does not match the winner of the final prediction")
        if response.final_ranking.runner_up != loser:
            warnings.append("Runner-up does not match the loser of the final prediction")
    else:
        warnings.append("No final knockout prediction found; champion/final validation skipped")

    third_place = next(
        (pred for pred in response.knockout_predictions if "third" in pred.stage.strip().lower()),
        None,
    )
    if third_place and response.final_ranking.third_place != third_place.predicted_winner:
        warnings.append("Third place does not match the winner of the third-place prediction")

    awards = response.awards_predictions
    if awards is None:
        warnings.append("awards_predictions is missing")
    else:
        for field_name, value in awards.model_dump().items():
            if not value:
                warnings.append(f"Optional award prediction missing: {field_name}")
    return response, errors, warnings
