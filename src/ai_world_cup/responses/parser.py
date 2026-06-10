from __future__ import annotations

import json
import re
from typing import Any

FENCED_JSON_RE = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.DOTALL | re.IGNORECASE)


def extract_json_text(raw_text: str) -> str:
    text = raw_text.strip()
    fenced = FENCED_JSON_RE.search(text)
    if fenced:
        return fenced.group(1).strip()
    if text.startswith("{") and text.endswith("}"):
        return text
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start : end + 1]
    raise ValueError("No JSON object found in response")


def parse_response_json(raw_text: str) -> dict[str, Any]:
    json_text = extract_json_text(raw_text)
    try:
        parsed = json.loads(json_text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON: {exc}") from exc
    if not isinstance(parsed, dict):
        raise ValueError("Response JSON must be an object")
    return parsed
