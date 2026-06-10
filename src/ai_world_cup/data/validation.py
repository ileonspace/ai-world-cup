from __future__ import annotations

from pydantic import BaseModel


class NormalizedTeam(BaseModel):
    source_name: str
    source_id: str | None = None
    name: str
    fifa_code: str | None = None
    country: str | None = None
    group_name: str | None = None
    logo_url: str | None = None


class NormalizedStadium(BaseModel):
    source_name: str
    source_id: str | None = None
    name: str
    city: str | None = None
    country: str | None = None
    capacity: int | None = None
    latitude: float | None = None
    longitude: float | None = None


class NormalizedMatch(BaseModel):
    source_name: str
    source_id: str | None = None
    match_number: int | None = None
    stage: str | None = None
    group_name: str | None = None
    home_team_name: str
    away_team_name: str
    kickoff_utc: str | None = None
    venue_name: str | None = None
    status: str = "SCHEDULED"
    home_score: int | None = None
    away_score: int | None = None
    raw: dict
