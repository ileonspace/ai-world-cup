from __future__ import annotations

import json
from pathlib import Path

from sqlmodel import Session, select

from ai_world_cup.responses.importer import get_or_create_model
from ai_world_cup.responses.parser import parse_response_json
from ai_world_cup.responses.tournament_validator import validate_tournament_response_data
from ai_world_cup.schemas import (
    PredictedAward,
    PredictedFinalRanking,
    PredictedGroupStanding,
    TournamentManualResponse,
    TournamentPrediction,
    TournamentPromptRun,
)


def import_tournament_response(
    session: Session,
    prompt_id: int,
    model_name: str,
    provider: str,
    response_file: Path,
    model_version: str | None = None,
) -> TournamentManualResponse:
    prompt = session.get(TournamentPromptRun, prompt_id)
    if not prompt:
        raise ValueError(f"No tournament prompt run found with id {prompt_id}")
    raw_text = response_file.read_text(encoding="utf-8")
    model = get_or_create_model(session, model_name, provider, model_version)
    parse_status = "VALID"
    messages: list[str] = []
    parsed = None
    response = None
    try:
        parsed = parse_response_json(raw_text)
        response, errors, warnings = validate_tournament_response_data(parsed, session)
        messages.extend(errors)
        messages.extend(f"WARNING: {warning}" for warning in warnings)
        if errors:
            parse_status = "INVALID"
        elif warnings:
            parse_status = "VALID_WITH_WARNINGS"
    except Exception as exc:  # noqa: BLE001 - stored for manual review
        parse_status = "INVALID"
        messages.append(str(exc))

    manual = TournamentManualResponse(
        tournament_prompt_run_id=prompt_id,
        model_id=model.id,
        response_file_path=str(response_file),
        raw_response_text=raw_text,
        parse_status=parse_status,
        validation_errors_json=json.dumps(messages),
    )
    session.add(manual)
    session.commit()
    session.refresh(manual)

    if response and parse_status != "INVALID":
        for pred in response.group_stage_predictions:
            session.add(
                TournamentPrediction(
                    tournament_manual_response_id=manual.id,
                    model_id=model.id,
                    match_number=pred.match_number,
                    stage=pred.stage,
                    group_name=pred.group,
                    home_team=pred.home_team,
                    away_team=pred.away_team,
                    predicted_home_goals=pred.predicted_home_goals,
                    predicted_away_goals=pred.predicted_away_goals,
                    predicted_outcome=pred.predicted_outcome.value,
                    predicted_winner=pred.predicted_winner,
                    confidence=pred.confidence,
                    reasoning_short=pred.reasoning_short,
                    is_official_fixture=True,
                )
            )
        for pred in response.knockout_predictions:
            session.add(
                TournamentPrediction(
                    tournament_manual_response_id=manual.id,
                    model_id=model.id,
                    match_number=pred.match_number,
                    stage=pred.stage,
                    group_name=None,
                    home_team=pred.home_team,
                    away_team=pred.away_team,
                    predicted_home_goals=pred.predicted_home_goals,
                    predicted_away_goals=pred.predicted_away_goals,
                    predicted_outcome=pred.predicted_outcome.value,
                    predicted_winner=pred.predicted_winner,
                    confidence=pred.confidence,
                    reasoning_short=pred.reasoning_short,
                    is_official_fixture=False,
                )
            )
        for standing in response.predicted_group_standings:
            session.add(
                PredictedGroupStanding(
                    tournament_manual_response_id=manual.id,
                    model_id=model.id,
                    group_name=standing.group,
                    rank=standing.rank,
                    team=standing.team,
                    points=standing.points,
                    goals_for=standing.goals_for,
                    goals_against=standing.goals_against,
                    goal_difference=standing.goal_difference,
                )
            )
        session.add(
            PredictedFinalRanking(
                tournament_manual_response_id=manual.id,
                model_id=model.id,
                champion=response.final_ranking.champion,
                runner_up=response.final_ranking.runner_up,
                third_place=response.final_ranking.third_place,
                fourth_place=response.final_ranking.fourth_place,
            )
        )
        awards = response.awards_predictions
        session.add(
            PredictedAward(
                tournament_manual_response_id=manual.id,
                model_id=model.id,
                top_scorer=awards.top_scorer if awards else None,
                best_player=awards.best_player if awards else None,
                best_young_player=awards.best_young_player if awards else None,
                best_goalkeeper=awards.best_goalkeeper if awards else None,
            )
        )
        session.commit()
    return manual


def revalidate_tournament_response(
    session: Session,
    response_id: int,
) -> TournamentManualResponse:
    manual = session.get(TournamentManualResponse, response_id)
    if not manual:
        raise ValueError(f"No tournament manual response found with id {response_id}")
    messages: list[str] = []
    parse_status = "VALID"
    try:
        parsed = parse_response_json(manual.raw_response_text)
        _, errors, warnings = validate_tournament_response_data(parsed, session)
        messages.extend(errors)
        messages.extend(f"WARNING: {warning}" for warning in warnings)
        if errors:
            parse_status = "INVALID"
        elif warnings:
            parse_status = "VALID_WITH_WARNINGS"
    except Exception as exc:  # noqa: BLE001
        parse_status = "INVALID"
        messages.append(str(exc))
    manual.parse_status = parse_status
    manual.validation_errors_json = json.dumps(messages)
    session.add(manual)
    session.commit()
    session.refresh(manual)
    return manual


def response_predictions(session: Session, response_id: int) -> list[TournamentPrediction]:
    return list(
        session.exec(
            select(TournamentPrediction).where(
                TournamentPrediction.tournament_manual_response_id == response_id
            )
        )
    )
