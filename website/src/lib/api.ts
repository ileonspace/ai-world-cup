import type {
  Fixture,
  GroupsPayload,
  KnockoutPayload,
  LeaderboardRow,
  ModelInfo,
  Prediction,
  ProjectSummary,
  SnapshotInfo,
  TournamentViewsPayload
} from './types';

async function loadJson<T>(name: string, fallback: T): Promise<T> {
  try {
    const response = await fetch(`${import.meta.env.BASE_URL}data/${name}`, {
      cache: 'no-cache'
    });
    if (!response.ok) return fallback;
    return (await response.json()) as T;
  } catch {
    return fallback;
  }
}

export const api = {
  summary: () =>
    loadJson<ProjectSummary>('project_summary.json', {
      project_name: 'AI World Cup',
      description: 'A reproducible benchmark for comparing LLM predictions on FIFA World Cup 2026.',
      latest_data_snapshot_id: null,
      prompt_version: 'v1',
      number_of_models: 0,
      number_of_predictions: 0,
      number_of_fixtures: 0,
      last_updated: ''
    }),
  leaderboard: () => loadJson<LeaderboardRow[]>('leaderboard.json', []),
  models: () => loadJson<ModelInfo[]>('models.json', []),
  fixtures: () => loadJson<Fixture[]>('fixtures.json', []),
  predictions: () => loadJson<Prediction[]>('predictions.json', []),
  groups: () =>
    loadJson<GroupsPayload>('groups.json', {
      official_groups: [],
      predicted_group_standings: [],
      actual_standings: []
    }),
  knockout: () =>
    loadJson<KnockoutPayload>('knockout.json', {
      predicted_knockout_brackets: [],
      final_ranking_predictions: [],
      champion_predictions: [],
      awards_predictions: []
    }),
  snapshots: () => loadJson<SnapshotInfo[]>('snapshots.json', []),
  tournamentViews: () =>
    loadJson<TournamentViewsPayload>('tournament_views.json', {
      sources: [],
      views: []
    })
};
