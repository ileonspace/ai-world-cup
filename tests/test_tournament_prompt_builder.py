from __future__ import annotations

from ai_world_cup.prompts.tournament_prompt_builder import build_tournament_prompt
from ai_world_cup.schemas import Match, Team


def test_build_tournament_prompt_contains_compact_context(session) -> None:
    session.add(Team(name="Mexico", group_name="A"))
    session.add(Team(name="South Africa", group_name="A"))
    session.add(
        Match(
            match_number=1,
            stage="Group Stage",
            group_name="A",
            home_team_name="Mexico",
            away_team_name="South Africa",
            venue_name="Estadio Azteca",
        )
    )
    session.commit()
    prompt, context = build_tournament_prompt(session, "v1")
    assert "AI World Cup" in prompt
    assert "predict the whole tournament" in prompt
    assert '"match_number":1' in prompt
    assert context["fixtures"][0]["home_team"] == "Mexico"
