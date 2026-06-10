# AI World Cup Full-Tournament Prediction Benchmark

You are participating in AI World Cup, a reproducible benchmark for FIFA World Cup 2026 predictions.

Prompt version: {{ prompt_version }}
Data snapshot ID: {{ data_snapshot_id }}

Task: predict the whole tournament from Match 1 through the Final using the provided teams, groups, fixtures, venues, and tournament structure.

Rules:
- Return JSON only.
- No markdown.
- No extra commentary.
- Do not invent statistics.
- If information is unavailable, say so briefly in reasoning fields.
- Keep every `reasoning_short` to 40 words or fewer.
- Group-stage matches may end in draws.
- Knockout matches cannot end in draws.
- Use match numbers from the fixture list where available.

Tournament structure:
- 48 teams.
- 12 groups of 4 teams.
- Group stage: each team plays the other teams in its group once.
- Knockout qualification: group winners, group runners-up, and the 8 best third-place teams advance to the Round of 32.
- Knockout rounds: Round of 32, Round of 16, Quarter-final, Semi-final, Third-place match, Final.

Teams:
{{ teams_json }}

Groups:
{{ groups_json }}

Venues:
{{ venues_json }}

Fixtures:
{{ fixtures_json }}

Return only this JSON object:

{
  "metadata": {
    "project": "AI World Cup",
    "prompt_version": "v1",
    "data_snapshot_id": "...",
    "model_name": "...",
    "provider": "...",
    "prediction_created_at": "YYYY-MM-DD"
  },
  "group_stage_predictions": [
    {
      "match_number": 1,
      "stage": "Group Stage",
      "group": "A",
      "home_team": "...",
      "away_team": "...",
      "predicted_home_goals": 0,
      "predicted_away_goals": 0,
      "predicted_outcome": "HOME_WIN|DRAW|AWAY_WIN",
      "predicted_winner": "team name or DRAW",
      "confidence": 0.0,
      "reasoning_short": "maximum 40 words"
    }
  ],
  "predicted_group_standings": [
    {
      "group": "A",
      "rank": 1,
      "team": "...",
      "points": 0,
      "goals_for": 0,
      "goals_against": 0,
      "goal_difference": 0
    }
  ],
  "knockout_predictions": [
    {
      "match_number": 73,
      "stage": "Round of 32",
      "home_team": "...",
      "away_team": "...",
      "predicted_home_goals": 0,
      "predicted_away_goals": 0,
      "predicted_outcome": "HOME_WIN|AWAY_WIN",
      "predicted_winner": "...",
      "confidence": 0.0,
      "reasoning_short": "maximum 40 words"
    }
  ],
  "final_ranking": {
    "champion": "...",
    "runner_up": "...",
    "third_place": "...",
    "fourth_place": "..."
  },
  "awards_predictions": {
    "top_scorer": "...",
    "best_player": "...",
    "best_young_player": "...",
    "best_goalkeeper": "..."
  }
}
