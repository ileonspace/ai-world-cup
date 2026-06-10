from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from ai_world_cup.data.validation import NormalizedMatch, NormalizedStadium, NormalizedTeam


def _pick(data: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in data and data[key] not in (None, ""):
            return data[key]
    return None


def _team_name(value: Any) -> str | None:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return _pick(
            value,
            "name",
            "name_en",
            "team",
            "team_name",
            "country",
            "country_en",
            "title",
            "fifa_name",
        )
    return None


def _as_list(value: Any, nested_key: str) -> list[Any]:
    if isinstance(value, list):
        return value
    if isinstance(value, dict):
        nested = value.get(nested_key)
        if isinstance(nested, list):
            return nested
    return []


def _int_or_none(value: Any) -> int | None:
    if value in (None, "", "null"):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def parse_datetime(value: Any) -> datetime | None:
    if not value:
        return None
    if isinstance(value, datetime):
        return value.astimezone(UTC) if value.tzinfo else value.replace(tzinfo=UTC)
    text = str(value).replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    return parsed.astimezone(UTC) if parsed.tzinfo else parsed.replace(tzinfo=UTC)


def normalize_openfootball(
    raw: dict[str, Any],
) -> tuple[list[NormalizedTeam], list[NormalizedMatch]]:
    payload = raw.get("payload", raw)
    teams: dict[str, NormalizedTeam] = {}
    matches: list[NormalizedMatch] = []
    rounds = payload.get("rounds", []) if isinstance(payload, dict) else []
    flat_matches = False
    if isinstance(payload, dict) and payload.get("matches"):
        flat_matches = True
        rounds = [{"name": "Group Stage", "matches": payload["matches"]}]
    for round_index, round_data in enumerate(rounds, start=1):
        stage = _pick(round_data, "name", "stage", "round") or f"Round {round_index}"
        group_name = stage if "group" in str(stage).lower() and stage != "Group Stage" else None
        for match_index, match in enumerate(round_data.get("matches", []), start=1):
            home = _team_name(_pick(match, "team1", "home_team", "homeTeam"))
            away = _team_name(_pick(match, "team2", "away_team", "awayTeam"))
            if not home or not away:
                continue
            match_group = _pick(match, "group", "group_name") or group_name
            for name in (home, away):
                teams.setdefault(
                    name,
                    NormalizedTeam(
                        source_name="openfootball",
                        source_id=name,
                        name=name,
                        country=name,
                        group_name=match_group,
                    ),
                )
            score = _pick(match, "score", "result") or {}
            home_score = (
                _pick(score, "ft1", "score1", "home", "team1") if isinstance(score, dict) else None
            )
            away_score = (
                _pick(score, "ft2", "score2", "away", "team2") if isinstance(score, dict) else None
            )
            matches.append(
                NormalizedMatch(
                    source_name="openfootball",
                    source_id=str(
                        _pick(match, "num", "number", "id") or f"{round_index}-{match_index}"
                    ),
                    match_number=_int_or_none(_pick(match, "num", "number"))
                    or (match_index if flat_matches else None),
                    stage=stage,
                    group_name=match_group,
                    home_team_name=home,
                    away_team_name=away,
                    kickoff_utc=_pick(match, "datetime", "kickoff", "date"),
                    venue_name=_team_name(_pick(match, "stadium", "venue", "ground")),
                    status="FINISHED"
                    if home_score is not None and away_score is not None
                    else "SCHEDULED",
                    home_score=home_score,
                    away_score=away_score,
                    raw=match,
                )
            )
    return list(teams.values()), matches


def normalize_worldcup26(
    raw: dict[str, Any],
) -> tuple[list[NormalizedTeam], list[NormalizedStadium], list[NormalizedMatch]]:
    payload = raw.get("payload", raw)
    teams_payload = _as_list(payload.get("teams", []), "teams") if isinstance(payload, dict) else []
    games_payload = _as_list(payload.get("games", []), "games") if isinstance(payload, dict) else []
    stadiums_payload = (
        _as_list(payload.get("stadiums", []), "stadiums") if isinstance(payload, dict) else []
    )
    stadium_names_by_id: dict[str, str] = {}
    teams: list[NormalizedTeam] = []
    for item in teams_payload or []:
        if not isinstance(item, dict):
            continue
        name = _pick(item, "name", "name_en", "team_name", "country", "country_en")
        if name:
            teams.append(
                NormalizedTeam(
                    source_name="worldcup26",
                    source_id=str(_pick(item, "id", "team_id") or name),
                    name=name,
                    fifa_code=_pick(item, "fifa_code", "code"),
                    country=_pick(item, "country", "country_en") or name,
                    group_name=_pick(item, "group", "group_name", "groups"),
                    logo_url=_pick(item, "logo", "flag", "logo_url"),
                )
            )
    stadiums: list[NormalizedStadium] = []
    for item in stadiums_payload or []:
        if not isinstance(item, dict):
            continue
        name = _pick(item, "name", "name_en", "stadium_name", "fifa_name")
        if name:
            source_id = str(_pick(item, "id", "stadium_id") or name)
            stadium_names_by_id[source_id] = name
            stadiums.append(
                NormalizedStadium(
                    source_name="worldcup26",
                    source_id=source_id,
                    name=name,
                    city=_pick(item, "city", "city_en"),
                    country=_pick(item, "country", "country_en"),
                    capacity=_pick(item, "capacity"),
                    latitude=_pick(item, "latitude", "lat"),
                    longitude=_pick(item, "longitude", "lng", "lon"),
                )
            )
    matches: list[NormalizedMatch] = []
    for item in games_payload or []:
        if not isinstance(item, dict):
            continue
        home = _team_name(_pick(item, "home_team", "home", "team1", "home_team_name_en"))
        away = _team_name(_pick(item, "away_team", "away", "team2", "away_team_name_en"))
        if not home or not away:
            continue
        finished = str(_pick(item, "finished", "status") or "").lower() in {
            "true",
            "finished",
            "ft",
        }
        home_score = _int_or_none(_pick(item, "home_score", "home_goals")) if finished else None
        away_score = _int_or_none(_pick(item, "away_score", "away_goals")) if finished else None
        stadium_id = _pick(item, "stadium_id")
        matches.append(
            NormalizedMatch(
                source_name="worldcup26",
                source_id=str(_pick(item, "id", "game_id", "match_number") or f"{home}-{away}"),
                match_number=_int_or_none(_pick(item, "match_number", "number", "id")),
                stage=_pick(item, "stage", "round", "type"),
                group_name=_pick(item, "group", "group_name"),
                home_team_name=home,
                away_team_name=away,
                kickoff_utc=_pick(item, "kickoff", "date", "datetime", "local_date"),
                venue_name=_team_name(_pick(item, "venue", "stadium"))
                or stadium_names_by_id.get(str(stadium_id)),
                status="FINISHED" if finished else "SCHEDULED",
                home_score=home_score,
                away_score=away_score,
                raw=item,
            )
        )
    return teams, stadiums, matches
