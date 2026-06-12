from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from sqlmodel import Session, select

from ai_world_cup.schemas import DataSnapshot, Match, Stadium, Team

TEMPLATE_PATH = Path(__file__).with_name("tournament_prediction_v1.md")

TEAM_ALIASES = {
    "Bosnia & Herzegovina": "Bosnia and Herzegovina",
    "USA": "United States",
    "U.S.A.": "United States",
    "United States of America": "United States",
    "DR Congo": "Democratic Republic of the Congo",
    "Congo DR": "Democratic Republic of the Congo",
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


def _canonical_group_name(group_name: str | None) -> str | None:
    if not group_name:
        return None
    return group_name.replace("Group ", "")


def _render_template(template: str, values: dict[str, str]) -> str:
    rendered = template
    for key, value in values.items():
        rendered = rendered.replace("{{ " + key + " }}", value)
    return rendered


def latest_snapshot_id(session: Session) -> int | None:
    snapshot = session.exec(select(DataSnapshot).order_by(DataSnapshot.id.desc())).first()
    return snapshot.id if snapshot else None


def tournament_context(session: Session) -> dict[str, Any]:
    teams = list(session.exec(select(Team).order_by(Team.group_name, Team.name)))
    matches = list(
        session.exec(select(Match).order_by(Match.match_number, Match.kickoff_utc, Match.id))
    )
    stadiums = list(session.exec(select(Stadium).order_by(Stadium.name)))
    groups: dict[str, list[str]] = {}
    teams_by_name: dict[str, dict[str, Any]] = {}
    for team in teams:
        group = _canonical_group_name(team.group_name)
        if not group:
            continue
        name = _canonical_team_name(team.name)
        if name not in groups.setdefault(group, []):
            groups[group].append(name)
        existing = teams_by_name.get(name, {})
        teams_by_name[name] = {
            "name": name,
            "fifa_code": existing.get("fifa_code") or team.fifa_code,
            "group": existing.get("group") or group,
            "country": _canonical_team_name(existing.get("country") or team.country or name),
            "confederation": existing.get("confederation") or team.confederation,
        }
    return {
        "data_snapshot_id": latest_snapshot_id(session),
        "teams": sorted(teams_by_name.values(), key=lambda item: (item["group"], item["name"])),
        "groups": [
            {"group": name, "teams": sorted(names)} for name, names in sorted(groups.items())
        ],
        "venues": [
            {
                "name": stadium.name,
                "city": stadium.city,
                "country": stadium.country,
                "capacity": stadium.capacity,
            }
            for stadium in stadiums
        ],
        "fixtures": [
            {
                "match_number": match.match_number,
                "stage": match.stage,
                "group": _canonical_group_name(match.group_name),
                "home_team": _canonical_team_name(match.home_team_name),
                "away_team": _canonical_team_name(match.away_team_name),
                "kickoff_utc": match.kickoff_utc.isoformat() if match.kickoff_utc else None,
                "venue": match.venue_name,
            }
            for match in matches
        ],
    }


def build_tournament_prompt(session: Session, version: str = "v1") -> tuple[str, dict[str, Any]]:
    if version != "v1":
        raise ValueError(f"Unsupported tournament prompt version: {version}")
    context = tournament_context(session)
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    compact = {
        key: json.dumps(value, ensure_ascii=True, separators=(",", ":"))
        for key, value in {
            "teams_json": context["teams"],
            "groups_json": context["groups"],
            "venues_json": context["venues"],
            "fixtures_json": context["fixtures"],
        }.items()
    }
    prompt = _render_template(
        template,
        {
            "prompt_version": version,
            "data_snapshot_id": str(context["data_snapshot_id"] or "Unavailable"),
            **compact,
        },
    )
    return prompt, context
