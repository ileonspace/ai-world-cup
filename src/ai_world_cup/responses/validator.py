from __future__ import annotations

from pydantic import ValidationError

from ai_world_cup.responses.response_schema import MatchPredictionResponse
from ai_world_cup.schemas import Match


def validate_match_response(data: dict, match: Match) -> MatchPredictionResponse:
    response = MatchPredictionResponse.model_validate(data)
    errors: list[str] = []
    if response.home_team != match.home_team_name:
        errors.append(f"home_team must match prompt match: {match.home_team_name}")
    if response.away_team != match.away_team_name:
        errors.append(f"away_team must match prompt match: {match.away_team_name}")
    if errors:
        raise ValueError("; ".join(errors))
    return response


def validation_errors_to_strings(exc: Exception) -> list[str]:
    if isinstance(exc, ValidationError):
        return [
            f"{'.'.join(str(part) for part in err['loc'])}: {err['msg']}" for err in exc.errors()
        ]
    return [str(exc)]
