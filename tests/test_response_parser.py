from __future__ import annotations

from ai_world_cup.responses.parser import parse_response_json


def test_parse_clean_json() -> None:
    parsed = parse_response_json('{"home_team":"Mexico"}')
    assert parsed["home_team"] == "Mexico"


def test_parse_markdown_fenced_json() -> None:
    parsed = parse_response_json('```json\n{"home_team":"Mexico"}\n```')
    assert parsed["home_team"] == "Mexico"
