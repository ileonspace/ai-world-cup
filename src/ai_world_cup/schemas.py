from __future__ import annotations

from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


def utcnow() -> datetime:
    return datetime.now(UTC)


class Team(SQLModel, table=True):
    __tablename__ = "teams"

    id: int | None = Field(default=None, primary_key=True)
    source_ids_json: str = "{}"
    name: str
    fifa_code: str | None = None
    country: str | None = None
    confederation: str | None = None
    group_name: str | None = None
    logo_url: str | None = None
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)


class Stadium(SQLModel, table=True):
    __tablename__ = "stadiums"

    id: int | None = Field(default=None, primary_key=True)
    source_ids_json: str = "{}"
    name: str
    city: str | None = None
    country: str | None = None
    capacity: int | None = None
    latitude: float | None = None
    longitude: float | None = None


class Match(SQLModel, table=True):
    __tablename__ = "matches"

    id: int | None = Field(default=None, primary_key=True)
    source_ids_json: str = "{}"
    match_number: int | None = None
    stage: str | None = None
    group_name: str | None = None
    home_team_id: int | None = Field(default=None, foreign_key="teams.id")
    away_team_id: int | None = Field(default=None, foreign_key="teams.id")
    home_team_name: str
    away_team_name: str
    kickoff_utc: datetime | None = None
    venue_name: str | None = None
    status: str = "SCHEDULED"
    home_score: int | None = None
    away_score: int | None = None
    winner_team_id: int | None = Field(default=None, foreign_key="teams.id")
    raw_json: str = "{}"
    data_snapshot_id: int | None = Field(default=None, foreign_key="data_snapshots.id")


class Standing(SQLModel, table=True):
    __tablename__ = "standings"

    id: int | None = Field(default=None, primary_key=True)
    group_name: str | None = None
    team_id: int | None = Field(default=None, foreign_key="teams.id")
    played: int = 0
    won: int = 0
    draw: int = 0
    lost: int = 0
    goals_for: int = 0
    goals_against: int = 0
    goal_difference: int = 0
    points: int = 0
    rank: int | None = None
    updated_at: datetime = Field(default_factory=utcnow)


class DataSnapshot(SQLModel, table=True):
    __tablename__ = "data_snapshots"

    id: int | None = Field(default=None, primary_key=True)
    source_name: str
    snapshot_hash: str
    raw_file_path: str
    created_at: datetime = Field(default_factory=utcnow)
    description: str | None = None


class PromptRun(SQLModel, table=True):
    __tablename__ = "prompt_runs"

    id: int | None = Field(default=None, primary_key=True)
    prompt_version: str
    prompt_type: str
    data_snapshot_id: int | None = Field(default=None, foreign_key="data_snapshots.id")
    created_at: datetime = Field(default_factory=utcnow)
    notes: str | None = None


class GeneratedPrompt(SQLModel, table=True):
    __tablename__ = "generated_prompts"

    id: int | None = Field(default=None, primary_key=True)
    prompt_run_id: int = Field(foreign_key="prompt_runs.id")
    match_id: int | None = Field(default=None, foreign_key="matches.id")
    prompt_type: str
    prompt_version: str
    prompt_text: str
    prompt_file_path: str
    created_at: datetime = Field(default_factory=utcnow)


class LLMModel(SQLModel, table=True):
    __tablename__ = "llm_models"

    id: int | None = Field(default=None, primary_key=True)
    model_display_name: str
    provider: str
    model_version: str | None = None
    access_mode: str = "manual"
    notes: str | None = None


class ManualResponse(SQLModel, table=True):
    __tablename__ = "manual_responses"

    id: int | None = Field(default=None, primary_key=True)
    generated_prompt_id: int = Field(foreign_key="generated_prompts.id")
    model_id: int = Field(foreign_key="llm_models.id")
    response_file_path: str
    raw_response_text: str
    imported_at: datetime = Field(default_factory=utcnow)
    parse_status: str
    validation_errors_json: str = "[]"


class Prediction(SQLModel, table=True):
    __tablename__ = "predictions"

    id: int | None = Field(default=None, primary_key=True)
    manual_response_id: int = Field(foreign_key="manual_responses.id")
    model_id: int = Field(foreign_key="llm_models.id")
    match_id: int = Field(foreign_key="matches.id")
    home_goals_pred: int | None = None
    away_goals_pred: int | None = None
    outcome_pred: str | None = None
    winner_team_name_pred: str | None = None
    confidence: float | None = None
    reasoning_short: str | None = None
    raw_json: str = "{}"
    parse_status: str


class EvaluationResult(SQLModel, table=True):
    __tablename__ = "evaluation_results"

    id: int | None = Field(default=None, primary_key=True)
    model_id: int = Field(foreign_key="llm_models.id")
    match_id: int = Field(foreign_key="matches.id")
    exact_score_points: int = 0
    outcome_points: int = 0
    goal_diff_points: int = 0
    winner_points: int = 0
    total_points: int = 0
    evaluated_at: datetime = Field(default_factory=utcnow)


class TournamentPromptRun(SQLModel, table=True):
    __tablename__ = "tournament_prompt_runs"

    id: int | None = Field(default=None, primary_key=True)
    prompt_version: str
    data_snapshot_id: int | None = Field(default=None, foreign_key="data_snapshots.id")
    prompt_file_path: str
    created_at: datetime = Field(default_factory=utcnow)
    notes: str | None = None


class TournamentManualResponse(SQLModel, table=True):
    __tablename__ = "tournament_manual_responses"

    id: int | None = Field(default=None, primary_key=True)
    tournament_prompt_run_id: int = Field(foreign_key="tournament_prompt_runs.id")
    model_id: int = Field(foreign_key="llm_models.id")
    response_file_path: str
    raw_response_text: str
    imported_at: datetime = Field(default_factory=utcnow)
    parse_status: str
    validation_errors_json: str = "[]"


class TournamentPrediction(SQLModel, table=True):
    __tablename__ = "tournament_predictions"

    id: int | None = Field(default=None, primary_key=True)
    tournament_manual_response_id: int = Field(foreign_key="tournament_manual_responses.id")
    model_id: int = Field(foreign_key="llm_models.id")
    match_number: int | None = None
    stage: str
    group_name: str | None = None
    home_team: str
    away_team: str
    predicted_home_goals: int
    predicted_away_goals: int
    predicted_outcome: str
    predicted_winner: str
    confidence: float
    reasoning_short: str
    is_official_fixture: bool = False
    created_at: datetime = Field(default_factory=utcnow)


class PredictedGroupStanding(SQLModel, table=True):
    __tablename__ = "predicted_group_standings"

    id: int | None = Field(default=None, primary_key=True)
    tournament_manual_response_id: int = Field(foreign_key="tournament_manual_responses.id")
    model_id: int = Field(foreign_key="llm_models.id")
    group_name: str
    rank: int
    team: str
    points: int
    goals_for: int
    goals_against: int
    goal_difference: int


class PredictedFinalRanking(SQLModel, table=True):
    __tablename__ = "predicted_final_rankings"

    id: int | None = Field(default=None, primary_key=True)
    tournament_manual_response_id: int = Field(foreign_key="tournament_manual_responses.id")
    model_id: int = Field(foreign_key="llm_models.id")
    champion: str
    runner_up: str
    third_place: str
    fourth_place: str


class PredictedAward(SQLModel, table=True):
    __tablename__ = "predicted_awards"

    id: int | None = Field(default=None, primary_key=True)
    tournament_manual_response_id: int = Field(foreign_key="tournament_manual_responses.id")
    model_id: int = Field(foreign_key="llm_models.id")
    top_scorer: str | None = None
    best_player: str | None = None
    best_young_player: str | None = None
    best_goalkeeper: str | None = None
