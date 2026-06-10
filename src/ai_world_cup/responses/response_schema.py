from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field, field_validator, model_validator


class Outcome(StrEnum):
    HOME_WIN = "HOME_WIN"
    DRAW = "DRAW"
    AWAY_WIN = "AWAY_WIN"


class MatchPredictionResponse(BaseModel):
    home_team: str
    away_team: str
    predicted_home_goals: int = Field(ge=0, le=15)
    predicted_away_goals: int = Field(ge=0, le=15)
    predicted_outcome: Outcome
    predicted_winner: str
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning_short: str

    @field_validator("reasoning_short")
    @classmethod
    def reasoning_max_80_words(cls, value: str) -> str:
        if len(value.split()) > 80:
            raise ValueError("reasoning_short must be maximum 80 words")
        return value

    @model_validator(mode="after")
    def score_consistency(self) -> MatchPredictionResponse:
        if self.predicted_home_goals > self.predicted_away_goals:
            expected_outcome = Outcome.HOME_WIN
            expected_winner = self.home_team
        elif self.predicted_home_goals < self.predicted_away_goals:
            expected_outcome = Outcome.AWAY_WIN
            expected_winner = self.away_team
        else:
            expected_outcome = Outcome.DRAW
            expected_winner = "DRAW"
        if self.predicted_outcome != expected_outcome:
            raise ValueError(
                f"predicted_outcome must be {expected_outcome} for score "
                f"{self.predicted_home_goals}-{self.predicted_away_goals}"
            )
        if self.predicted_winner != expected_winner:
            raise ValueError(f"predicted_winner must be {expected_winner} for the predicted score")
        return self
