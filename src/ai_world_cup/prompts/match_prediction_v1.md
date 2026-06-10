# AI World Cup Match Prediction Benchmark

You are participating in AI World Cup, a reproducible prediction benchmark for FIFA World Cup 2026.

Every model receives the same data context and the same prompt template. Use only the information provided here and your general football knowledge. Do not invent statistics. If information is unavailable, say so briefly in `reasoning_short`.

## Benchmark Metadata

- Prompt version: {{ prompt_version }}
- Prompt type: match_prediction
- Data snapshot ID: {{ data_snapshot_id }}
- Match ID: {{ match_id }}

## Match

- Match date/time UTC: {{ kickoff_utc }}
- Stage/group: {{ stage_group }}
- Venue/city: {{ venue }}
- Home team: {{ home_team }}
- Away team: {{ away_team }}

## Current Group Standings

{{ standings }}

## Historical World Cup Context

{{ historical_context }}

## Available Team Data

Home team data:
{{ home_team_data }}

Away team data:
{{ away_team_data }}

## Output Rules

- Return strict JSON only.
- Do not use markdown.
- Do not include commentary outside JSON.
- `predicted_home_goals` and `predicted_away_goals` must be integers from 0 to 15.
- `predicted_outcome` must be one of `HOME_WIN`, `DRAW`, or `AWAY_WIN`.
- `predicted_winner` must be the winning team name or `DRAW`.
- `confidence` must be a number from 0 to 1.
- `reasoning_short` must be no more than 80 words.

Return only this JSON object:

{
  "home_team": "...",
  "away_team": "...",
  "predicted_home_goals": 0,
  "predicted_away_goals": 0,
  "predicted_outcome": "HOME_WIN|DRAW|AWAY_WIN",
  "predicted_winner": "team name or DRAW",
  "confidence": 0.0,
  "reasoning_short": "maximum 80 words"
}
