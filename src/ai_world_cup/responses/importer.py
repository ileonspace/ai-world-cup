from __future__ import annotations

import json
from pathlib import Path

from sqlmodel import Session, select

from ai_world_cup.responses.parser import parse_response_json
from ai_world_cup.responses.validator import validate_match_response, validation_errors_to_strings
from ai_world_cup.schemas import GeneratedPrompt, LLMModel, ManualResponse, Match, Prediction

PROVIDER_ALIASES = {
    "Mistral": "Mistral AI",
}


def get_or_create_model(
    session: Session,
    model_name: str,
    provider: str,
    model_version: str | None = None,
) -> LLMModel:
    provider = PROVIDER_ALIASES.get(provider, provider)
    model = session.exec(
        select(LLMModel).where(
            LLMModel.model_display_name == model_name,
            LLMModel.provider == provider,
            LLMModel.model_version == model_version,
        )
    ).first()
    if model:
        return model
    model = LLMModel(
        model_display_name=model_name,
        provider=provider,
        model_version=model_version,
        access_mode="manual",
    )
    session.add(model)
    session.commit()
    session.refresh(model)
    return model


def import_manual_response(
    session: Session,
    prompt_id: int,
    model_name: str,
    provider: str,
    response_file: Path,
    model_version: str | None = None,
) -> ManualResponse:
    prompt = session.get(GeneratedPrompt, prompt_id)
    if not prompt:
        raise ValueError(f"No generated prompt found with id {prompt_id}")
    if prompt.match_id is None:
        raise ValueError("Only match prediction responses are supported")
    match = session.get(Match, prompt.match_id)
    if not match:
        raise ValueError(f"No match found for prompt {prompt_id}")
    raw_text = response_file.read_text(encoding="utf-8")
    model = get_or_create_model(session, model_name, provider, model_version)
    parse_status = "VALID"
    validation_errors: list[str] = []
    parsed: dict = {}
    prediction_values = None
    try:
        parsed = parse_response_json(raw_text)
        prediction_values = validate_match_response(parsed, match)
    except Exception as exc:  # noqa: BLE001 - persisted as validation report for manual workflow
        parse_status = "INVALID"
        validation_errors = validation_errors_to_strings(exc)
    manual = ManualResponse(
        generated_prompt_id=prompt_id,
        model_id=model.id,
        response_file_path=str(response_file),
        raw_response_text=raw_text,
        parse_status=parse_status,
        validation_errors_json=json.dumps(validation_errors),
    )
    session.add(manual)
    session.commit()
    session.refresh(manual)
    if prediction_values:
        prediction = Prediction(
            manual_response_id=manual.id,
            model_id=model.id,
            match_id=match.id,
            home_goals_pred=prediction_values.predicted_home_goals,
            away_goals_pred=prediction_values.predicted_away_goals,
            outcome_pred=prediction_values.predicted_outcome.value,
            winner_team_name_pred=prediction_values.predicted_winner,
            confidence=prediction_values.confidence,
            reasoning_short=prediction_values.reasoning_short,
            raw_json=json.dumps(parsed, sort_keys=True),
            parse_status="VALID",
        )
        session.add(prediction)
        session.commit()
    return manual
