from __future__ import annotations

import json
from pathlib import Path

from sqlmodel import select

from ai_world_cup.responses.tournament_importer import import_tournament_response
from ai_world_cup.schemas import Match, TournamentPrediction, TournamentPromptRun

FIXTURES = Path(__file__).parent / "fixtures"


def test_import_tournament_response_from_markdown_fence(session, tmp_path) -> None:
    session.add(
        Match(
            match_number=1,
            stage="Group Stage",
            group_name="A",
            home_team_name="Mexico",
            away_team_name="South Africa",
        )
    )
    prompt = TournamentPromptRun(
        prompt_version="v1", data_snapshot_id=1, prompt_file_path="prompt.md"
    )
    session.add(prompt)
    session.commit()
    session.refresh(prompt)
    payload = json.loads((FIXTURES / "sample_tournament_response_valid.json").read_text())
    response_file = tmp_path / "response.md"
    response_file.write_text("```json\n" + json.dumps(payload) + "\n```", encoding="utf-8")
    manual = import_tournament_response(
        session,
        prompt_id=prompt.id,
        model_name="Model A",
        provider="Provider",
        response_file=response_file,
    )
    predictions = list(session.exec(select(TournamentPrediction)))
    assert manual.parse_status == "VALID"
    assert len(predictions) == 3
