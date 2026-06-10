from __future__ import annotations

import json
from pathlib import Path

from sqlmodel import Session, select

from ai_world_cup.schemas import Match, Standing, Team

TEMPLATE_PATH = Path(__file__).with_name("match_prediction_v1.md")


def _render_template(template: str, values: dict[str, str]) -> str:
    rendered = template
    for key, value in values.items():
        rendered = rendered.replace("{{ " + key + " }}", value)
    return rendered


def _team_json(team: Team | None) -> str:
    if not team:
        return "Unavailable"
    return json.dumps(
        {
            "name": team.name,
            "fifa_code": team.fifa_code,
            "country": team.country,
            "confederation": team.confederation,
            "group_name": team.group_name,
        },
        indent=2,
        sort_keys=True,
    )


def _standings_text(standings: list[Standing]) -> str:
    if not standings:
        return "Unavailable"
    rows = [
        {
            "rank": item.rank,
            "team_id": item.team_id,
            "played": item.played,
            "points": item.points,
            "goal_difference": item.goal_difference,
        }
        for item in standings
    ]
    return json.dumps(rows, indent=2, sort_keys=True)


def build_match_prompt(session: Session, match_id: int, version: str = "v1") -> str:
    if version != "v1":
        raise ValueError(f"Unsupported match prompt version: {version}")
    match = session.get(Match, match_id)
    if not match:
        raise ValueError(f"No match found with id {match_id}")
    home_team = session.get(Team, match.home_team_id) if match.home_team_id else None
    away_team = session.get(Team, match.away_team_id) if match.away_team_id else None
    standings = list(session.exec(select(Standing).where(Standing.group_name == match.group_name)))
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    return _render_template(
        template,
        {
            "prompt_version": version,
            "data_snapshot_id": str(match.data_snapshot_id or "Unavailable"),
            "match_id": str(match.id),
            "kickoff_utc": match.kickoff_utc.isoformat() if match.kickoff_utc else "Unavailable",
            "stage_group": match.group_name or match.stage or "Unavailable",
            "venue": match.venue_name or "Unavailable",
            "home_team": match.home_team_name,
            "away_team": match.away_team_name,
            "standings": _standings_text(standings),
            "historical_context": "Unavailable in the current database snapshot.",
            "home_team_data": _team_json(home_team),
            "away_team_data": _team_json(away_team),
        },
    )
