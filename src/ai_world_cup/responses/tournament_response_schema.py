from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field, field_validator, model_validator


class MatchOutcome(StrEnum):
    HOME_WIN = "HOME_WIN"
    DRAW = "DRAW"
    AWAY_WIN = "AWAY_WIN"


class KnockoutOutcome(StrEnum):
    HOME_WIN = "HOME_WIN"
    AWAY_WIN = "AWAY_WIN"


class TournamentMetadata(BaseModel):
    project: str
    prompt_version: str
    data_snapshot_id: str
    model_name: str
    provider: str
    prediction_created_at: str


class TournamentMatchPrediction(BaseModel):
    match_number: int | None = None
    stage: str
    group: str | None = None
    home_team: str
    away_team: str
    predicted_home_goals: int = Field(ge=0, le=15)
    predicted_away_goals: int = Field(ge=0, le=15)
    predicted_outcome: MatchOutcome
    predicted_winner: str
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning_short: str

    @field_validator("reasoning_short")
    @classmethod
    def reasoning_max_40_words(cls, value: str) -> str:
        if len(value.split()) > 40:
            raise ValueError("reasoning_short must be maximum 40 words")
        return value

    @model_validator(mode="after")
    def score_consistency(self) -> TournamentMatchPrediction:
        if self.predicted_home_goals > self.predicted_away_goals:
            expected_outcome = MatchOutcome.HOME_WIN
            expected_winner = self.home_team
        elif self.predicted_home_goals < self.predicted_away_goals:
            expected_outcome = MatchOutcome.AWAY_WIN
            expected_winner = self.away_team
        else:
            expected_outcome = MatchOutcome.DRAW
            expected_winner = "DRAW"
        if self.predicted_outcome != expected_outcome:
            raise ValueError(
                f"predicted_outcome must be {expected_outcome} for score "
                f"{self.predicted_home_goals}-{self.predicted_away_goals}"
            )
        if self.predicted_winner != expected_winner:
            raise ValueError(f"predicted_winner must be {expected_winner} for the predicted score")
        return self


class KnockoutMatchPrediction(BaseModel):
    match_number: int | None = None
    stage: str
    home_team: str
    away_team: str
    predicted_home_goals: int = Field(ge=0, le=15)
    predicted_away_goals: int = Field(ge=0, le=15)
    predicted_outcome: MatchOutcome
    predicted_winner: str
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning_short: str

    @field_validator("reasoning_short")
    @classmethod
    def reasoning_max_40_words(cls, value: str) -> str:
        if len(value.split()) > 40:
            raise ValueError("reasoning_short must be maximum 40 words")
        return value

    @model_validator(mode="after")
    def knockout_consistency(self) -> KnockoutMatchPrediction:
        if self.predicted_home_goals > self.predicted_away_goals:
            expected_outcome = MatchOutcome.HOME_WIN
        elif self.predicted_home_goals < self.predicted_away_goals:
            expected_outcome = MatchOutcome.AWAY_WIN
        elif self.predicted_winner == self.home_team:
            expected_outcome = MatchOutcome.HOME_WIN
        elif self.predicted_winner == self.away_team:
            expected_outcome = MatchOutcome.AWAY_WIN
        else:
            raise ValueError("Knockout predictions cannot have DRAW as the winner")
        if self.predicted_outcome != expected_outcome:
            raise ValueError(
                f"predicted_outcome must be {expected_outcome} for score "
                f"{self.predicted_home_goals}-{self.predicted_away_goals}"
            )
        if self.predicted_winner == "DRAW":
            raise ValueError("Knockout predicted_winner must be a team, not DRAW")
        return self


class PredictedGroupStandingItem(BaseModel):
    group: str
    rank: int = Field(ge=1)
    team: str
    points: int = Field(ge=0)
    goals_for: int = Field(ge=0)
    goals_against: int = Field(ge=0)
    goal_difference: int


class FinalRanking(BaseModel):
    champion: str
    runner_up: str
    third_place: str
    fourth_place: str


class AwardsPredictions(BaseModel):
    top_scorer: str | None = None
    best_player: str | None = None
    best_young_player: str | None = None
    best_goalkeeper: str | None = None


class TournamentPredictionResponse(BaseModel):
    metadata: TournamentMetadata
    group_stage_predictions: list[TournamentMatchPrediction]
    predicted_group_standings: list[PredictedGroupStandingItem]
    knockout_predictions: list[KnockoutMatchPrediction]
    final_ranking: FinalRanking
    awards_predictions: AwardsPredictions | None = None
