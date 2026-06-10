# Prompt Protocol

Prompts are generated from versioned templates in `src/ai_world_cup/prompts/`.

The recommended workflow uses `tournament_prediction_v1.md`, which produces one full-tournament prompt for each model. The prompt includes:

- Project name.
- Prompt version.
- Data snapshot ID.
- Full list of teams.
- Full groups.
- Group-stage fixture list.
- Match numbers.
- Kickoff dates and times where available.
- Venues where available.
- Tournament rules and structure.
- Knockout qualification rules.
- Strict JSON-only output rules.

The optional match-by-match workflow still uses `match_prediction_v1.md`. For match prediction v1, the prompt includes:

- Project name.
- Benchmark instructions.
- Match date and time.
- Stage or group.
- Venue where available.
- Home and away teams.
- Current group standings where available.
- Historical context where available.
- Team data from the local database.
- Data snapshot ID.
- Prompt version.
- Strict JSON-only output rules.

Do not edit generated prompt files before submitting them to models. If the template changes, increment the prompt version and keep old prompts for reproducibility.
