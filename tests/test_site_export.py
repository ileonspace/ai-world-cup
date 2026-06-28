from __future__ import annotations

from ai_world_cup.schemas import Match, Team
from ai_world_cup.site_export import _tournament_views_payload


def test_actual_tournament_view_includes_round_of_32_matches(session) -> None:
    session.add(Team(name="South Africa", group_name="A", fifa_code="RSA"))
    session.add(Team(name="Canada", group_name="B", fifa_code="CAN"))
    session.add(
        Match(
            match_number=73,
            stage="r32",
            group_name="R32",
            home_team_name="South Africa",
            away_team_name="Canada",
        )
    )
    session.commit()

    payload = _tournament_views_payload(session)
    actual = next(view for view in payload["views"] if view["source"]["id"] == "actual")
    round_of_32 = next(
        round_view
        for round_view in actual["knockout_rounds"]
        if round_view["stage"] == "Round of 32"
    )

    assert round_of_32["matches"] == [
        {
            "match_number": 73,
            "stage": "Round of 32",
            "home_team": "South Africa",
            "away_team": "Canada",
            "home_score": None,
            "away_score": None,
            "winner": None,
        }
    ]
