import { useEffect, useMemo, useState } from 'react';
import { ChartCard } from '../components/ChartCard';
import { LeaderboardTable } from '../components/LeaderboardTable';
import { ConfidenceChart } from '../charts/ConfidenceChart';
import { ExactScoreChart } from '../charts/ExactScoreChart';
import { LeaderboardBarChart } from '../charts/LeaderboardBarChart';
import { OutcomeAccuracyChart } from '../charts/OutcomeAccuracyChart';
import { api } from '../lib/api';
import type { LeaderboardRow, ModelInfo, TournamentGroupTable, TournamentView } from '../lib/types';
import { unique } from '../lib/utils';

type QualificationRow = {
  modelName: string;
  provider: string;
  predictedTeams: number;
  correctTeams: number;
  qualificationPoints: number;
  roundOf32ReachPoints: number;
  groupWinnerPoints: number;
  topTwoPoints: number;
  exactRankPoints: number;
  totalPhasePoints: number;
};

function teamsInRound(view: TournamentView, stage: string): Set<string> {
  const round = view.knockout_rounds.find((item) => item.stage === stage);
  return new Set(round?.matches.flatMap((match) => [match.home_team, match.away_team]) ?? []);
}

function groupTablesByName(view: TournamentView): Map<string, TournamentGroupTable> {
  return new Map(view.group_tables.map((table) => [table.group, table]));
}

function sameTeamSet(left: string[], right: string[]): boolean {
  if (left.length !== right.length) return false;
  const rightSet = new Set(right);
  return left.every((team) => rightSet.has(team));
}

function qualificationRows(views: TournamentView[]): QualificationRow[] {
  const actual = views.find((view) => view.source.kind === 'actual');
  if (!actual) return [];
  const actualRoundOf32Teams = teamsInRound(actual, 'Round of 32');
  const actualGroups = groupTablesByName(actual);

  return views
    .filter((view) => view.source.kind === 'model')
    .map((view) => {
      const predictedRoundOf32Teams = teamsInRound(view, 'Round of 32');
      const correctTeams = Array.from(predictedRoundOf32Teams).filter((teamName) =>
        actualRoundOf32Teams.has(teamName)
      ).length;
      const modelGroups = groupTablesByName(view);
      let groupWinnerPoints = 0;
      let topTwoPoints = 0;
      let exactRankPoints = 0;

      actualGroups.forEach((actualTable, groupName) => {
        const modelTable = modelGroups.get(groupName);
        if (!modelTable) return;
        const actualTeams = actualTable.rows.map((row) => row.team);
        const modelTeams = modelTable.rows.map((row) => row.team);
        if (actualTeams[0] && actualTeams[0] === modelTeams[0]) {
          groupWinnerPoints += 5;
        }
        if (sameTeamSet(actualTeams.slice(0, 2), modelTeams.slice(0, 2))) {
          topTwoPoints += 5;
        }
        actualTeams.forEach((teamName, index) => {
          if (modelTeams[index] === teamName) {
            exactRankPoints += 2;
          }
        });
      });

      const qualificationPoints = correctTeams * 3;
      return {
        modelName: view.source.label,
        provider: view.source.provider,
        predictedTeams: predictedRoundOf32Teams.size,
        correctTeams,
        qualificationPoints,
        roundOf32ReachPoints: correctTeams * 2,
        groupWinnerPoints,
        topTwoPoints,
        exactRankPoints,
        totalPhasePoints:
          groupWinnerPoints +
          topTwoPoints +
          qualificationPoints +
          exactRankPoints +
          correctTeams * 2,
      };
    })
    .sort((a, b) =>
      b.correctTeams - a.correctTeams ||
      b.totalPhasePoints - a.totalPhasePoints ||
      a.modelName.localeCompare(b.modelName)
    );
}

export function Leaderboard() {
  const [rows, setRows] = useState<LeaderboardRow[]>([]);
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [tournamentViews, setTournamentViews] = useState<TournamentView[]>([]);
  const [provider, setProvider] = useState('');
  const [webSearch, setWebSearch] = useState('');
  const [query, setQuery] = useState('');

  useEffect(() => {
    void Promise.all([api.leaderboard(), api.models(), api.tournamentViews()]).then(([leaderboardRows, modelRows, tournamentPayload]) => {
      setRows(leaderboardRows);
      setModels(modelRows);
      setTournamentViews(tournamentPayload.views);
    });
  }, []);

  const providers = unique(rows.map((row) => row.provider)).sort();
  const modelByName = new Map(models.map((model) => [model.model_display_name, model]));
  const filtered = useMemo(
    () =>
      rows.filter(
        (row) => {
          const model = modelByName.get(row.model_name);
          const searchValue =
            model?.web_search_enabled === true
              ? 'enabled'
              : model?.web_search_enabled === false
                ? 'disabled'
                : 'unknown';
          return (
            (!provider || row.provider === provider) &&
            (!webSearch || searchValue === webSearch) &&
            (!query || row.model_name.toLowerCase().includes(query.toLowerCase()))
          );
        }
      ),
    [rows, provider, query, webSearch, modelByName]
  );
  const qualificationSummary = useMemo(
    () =>
      qualificationRows(tournamentViews).filter((row) =>
        (!provider || row.provider === provider) &&
        (!query || row.modelName.toLowerCase().includes(query.toLowerCase()))
      ),
    [provider, query, tournamentViews]
  );

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Tournament leaderboard</h1>
        <p className="mt-2 text-slate-600 dark:text-slate-300">Sortable model rankings from exported tournament prediction data.</p>
      </div>
      <div className="flex flex-wrap gap-3">
        <input className="rounded-md border border-slate-300 bg-white px-3 py-2 dark:border-slate-700 dark:bg-slate-950" placeholder="Search model" value={query} onChange={(event) => setQuery(event.target.value)} />
        <select className="rounded-md border border-slate-300 bg-white px-3 py-2 dark:border-slate-700 dark:bg-slate-950" value={provider} onChange={(event) => setProvider(event.target.value)}>
          <option value="">All providers</option>
          {providers.map((item) => <option key={item}>{item}</option>)}
        </select>
        <select className="rounded-md border border-slate-300 bg-white px-3 py-2 dark:border-slate-700 dark:bg-slate-950" value={webSearch} onChange={(event) => setWebSearch(event.target.value)}>
          <option value="">All search settings</option>
          <option value="enabled">Web search enabled</option>
          <option value="disabled">Web search disabled</option>
          <option value="unknown">Web search unknown</option>
        </select>
      </div>
      <div className="grid gap-4 lg:grid-cols-2">
        <ChartCard title="Total points"><LeaderboardBarChart data={filtered} /></ChartCard>
        <ChartCard title="Outcome accuracy"><OutcomeAccuracyChart data={filtered} /></ChartCard>
        <ChartCard title="Exact score accuracy"><ExactScoreChart data={filtered} /></ChartCard>
        <ChartCard title="Average confidence"><ConfidenceChart data={filtered} /></ChartCard>
      </div>
      {qualificationSummary.length ? (
        <section className="rounded-lg border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-950">
          <div className="border-b border-slate-100 p-4 dark:border-slate-800">
            <h2 className="text-xl font-semibold">Group stage to Round of 32</h2>
            <p className="mt-1 text-sm text-slate-600 dark:text-slate-300">
              Correct qualified teams are counted against the real Round of 32. Points follow the scoring rules for group winners, top two, qualified teams, exact ranks, and teams reaching the Round of 32.
            </p>
          </div>
          <div className="table-scroll">
            <table className="min-w-full text-left text-sm">
              <thead className="bg-slate-50 text-slate-600 dark:bg-slate-900 dark:text-slate-300">
                <tr>
                  {['Model', 'Predicted R32', 'Correct R32', 'Qualified pts', 'R32 reach pts', 'Group winner pts', 'Top-two pts', 'Exact-rank pts', 'Phase total'].map((head) => (
                    <th key={head} className="px-4 py-3 font-semibold">{head}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {qualificationSummary.map((row) => (
                  <tr key={row.modelName} className="border-t border-slate-100 dark:border-slate-800">
                    <td className="px-4 py-3">
                      <div className="font-semibold">{row.modelName}</div>
                      <div className="text-xs text-slate-500 dark:text-slate-400">{row.provider}</div>
                    </td>
                    <td className="px-4 py-3">{row.predictedTeams}/32</td>
                    <td className="px-4 py-3 font-semibold">{row.correctTeams}/32</td>
                    <td className="px-4 py-3">{row.qualificationPoints}</td>
                    <td className="px-4 py-3">{row.roundOf32ReachPoints}</td>
                    <td className="px-4 py-3">{row.groupWinnerPoints}</td>
                    <td className="px-4 py-3">{row.topTwoPoints}</td>
                    <td className="px-4 py-3">{row.exactRankPoints}</td>
                    <td className="px-4 py-3 font-semibold">{row.totalPhasePoints}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      ) : null}
      <LeaderboardTable data={filtered} />
    </div>
  );
}
