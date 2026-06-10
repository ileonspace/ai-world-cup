# Methodology

AI World Cup benchmarks model predictions by controlling the prompt, data snapshot, and response schema.

The repository fetches football data from supported football data sources, stores immutable raw snapshots, normalizes fixtures and teams into SQLite, and generates prompt files from a versioned template. Each model receives the same prompt text for a given match, prompt version, and data snapshot.

The repository does not call LLM APIs. Manual submission is part of the benchmark design so models from different providers and interfaces can be compared without integrating provider-specific clients.

Fair comparisons require:

- Same generated prompt text.
- Same prompt version.
- Same data snapshot ID.
- Same model access date where possible.
- Raw responses saved exactly as returned.
- No manual correction before import.
