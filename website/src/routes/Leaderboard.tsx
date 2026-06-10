import { useEffect, useMemo, useState } from 'react';
import { ChartCard } from '../components/ChartCard';
import { LeaderboardTable } from '../components/LeaderboardTable';
import { ConfidenceChart } from '../charts/ConfidenceChart';
import { ExactScoreChart } from '../charts/ExactScoreChart';
import { LeaderboardBarChart } from '../charts/LeaderboardBarChart';
import { OutcomeAccuracyChart } from '../charts/OutcomeAccuracyChart';
import { api } from '../lib/api';
import type { LeaderboardRow, ModelInfo } from '../lib/types';
import { unique } from '../lib/utils';

export function Leaderboard() {
  const [rows, setRows] = useState<LeaderboardRow[]>([]);
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [provider, setProvider] = useState('');
  const [webSearch, setWebSearch] = useState('');
  const [query, setQuery] = useState('');

  useEffect(() => {
    void Promise.all([api.leaderboard(), api.models()]).then(([leaderboardRows, modelRows]) => {
      setRows(leaderboardRows);
      setModels(modelRows);
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
      <LeaderboardTable data={filtered} />
    </div>
  );
}
