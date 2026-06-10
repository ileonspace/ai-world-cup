from __future__ import annotations

from ai_world_cup.prompts.prompt_builder import build_match_prompt
from ai_world_cup.schemas import Match, Team


def test_build_match_prompt_contains_protocol_fields(session) -> None:
    home = Team(name="Mexico", country="Mexico", group_name="A")
    away = Team(name="South Africa", country="South Africa", group_name="A")
    session.add(home)
    session.add(away)
    session.commit()
    session.refresh(home)
    session.refresh(away)
    match = Match(
        home_team_id=home.id,
        away_team_id=away.id,
        home_team_name="Mexico",
        away_team_name="South Africa",
        group_name="A",
        stage="Group stage",
        venue_name="Estadio Azteca",
        data_snapshot_id=7,
    )
    session.add(match)
    session.commit()
    session.refresh(match)
    prompt = build_match_prompt(session, match.id, "v1")
    assert "AI World Cup" in prompt
    assert "Data snapshot ID: 7" in prompt
    assert "Return only this JSON object" in prompt
    assert "No markdown" in prompt or "Do not use markdown" in prompt
