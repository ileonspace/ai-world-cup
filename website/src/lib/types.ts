export type ProjectSummary = {
  project_name: string;
  description: string;
  latest_data_snapshot_id: number | null;
  prompt_version: string;
  number_of_models: number;
  number_of_predictions: number;
  number_of_fixtures: number;
  last_updated: string;
};

export type LeaderboardRow = {
  rank: number;
  model_name: string;
  provider: string;
  total_points: number;
  group_stage_points: number;
  group_standing_points: number;
  knockout_points: number;
  exact_score_accuracy: number;
  outcome_accuracy: number;
  average_confidence: number;
  champion_prediction: string;
};

export type ModelInfo = {
  id: number;
  model_display_name: string;
  provider: string;
  access_mode: string;
  web_search_enabled: boolean | null;
  submitted_at: string | null;
  notes: string | null;
};

export type Fixture = {
  match_number: number | null;
  stage: string | null;
  group: string | null;
  home_team: string;
  away_team: string;
  kickoff_time: string | null;
  venue: string | null;
  status: string;
  home_score: number | null;
  away_score: number | null;
  winner: string | null;
};

export type Prediction = {
  model_name: string;
  provider: string;
  match_number: number | null;
  stage: string;
  home_team: string;
  away_team: string;
  predicted_home_goals: number;
  predicted_away_goals: number;
  predicted_outcome: string;
  predicted_winner: string;
  confidence: number;
  reasoning_short: string;
  points: number | null;
};

export type GroupsPayload = {
  official_groups: { group: string; teams: string[] }[];
  predicted_group_standings: {
    model_name: string;
    provider: string;
    group: string;
    rank: number;
    team: string;
    points: number;
    goals_for: number;
    goals_against: number;
    goal_difference: number;
  }[];
  actual_standings: unknown[];
};

export type KnockoutPayload = {
  predicted_knockout_brackets: {
    model_name: string;
    provider: string;
    match_number: number | null;
    stage: string;
    home_team: string;
    away_team: string;
    predicted_winner: string;
    confidence: number;
  }[];
  final_ranking_predictions: {
    model_name: string;
    provider: string;
    champion: string;
    runner_up: string;
    third_place: string;
    fourth_place: string;
  }[];
  champion_predictions: { team: string; count: number }[];
  awards_predictions: unknown[];
};

export type SnapshotInfo = {
  data_snapshot_id: number;
  source_name: string;
  created_at: string;
  raw_file_path: string;
  prompt_version: string | null;
};

export type TournamentSource = {
  id: string;
  label: string;
  provider: string;
  kind: 'actual' | 'model';
};

export type TournamentGroupRow = {
  rank: number;
  team: string;
  fifa_code: string | null;
  country: string | null;
  matches_played: number;
  wins: number;
  draws: number;
  losses: number;
  goals_for: number;
  goals_against: number;
  goal_difference: number;
  points: number;
};

export type TournamentGroupTable = {
  group: string;
  rows: TournamentGroupRow[];
};

export type TournamentBracketMatch = {
  match_number: number | null;
  stage: string;
  home_team: string;
  away_team: string;
  home_score: number | null;
  away_score: number | null;
  winner: string | null;
};

export type TournamentBracketRound = {
  stage: string;
  matches: TournamentBracketMatch[];
};

export type TournamentView = {
  source: TournamentSource;
  group_tables: TournamentGroupTable[];
  knockout_rounds: TournamentBracketRound[];
  final_ranking: {
    champion: string;
    runner_up: string;
    third_place: string;
    fourth_place: string;
  } | null;
};

export type TournamentViewsPayload = {
  sources: TournamentSource[];
  views: TournamentView[];
};
