import { useEffect, useState } from 'react';
import { ChartCard } from '../components/ChartCard';
import { LeaderboardTable } from '../components/LeaderboardTable';
import { ModelCard } from '../components/ModelCard';
import { ConfidenceChart } from '../charts/ConfidenceChart';
import { LeaderboardBarChart } from '../charts/LeaderboardBarChart';
import { api } from '../lib/api';
import type { LeaderboardRow, ModelInfo } from '../lib/types';

export function ModelComparison() {
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [leaderboard, setLeaderboard] = useState<LeaderboardRow[]>([]);
  useEffect(() => {
    void Promise.all([api.models(), api.leaderboard()]).then(([m, l]) => {
      setModels(m);
      setLeaderboard(l);
    });
  }, []);
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Model comparison</h1>
      <div className="grid gap-4 md:grid-cols-3">
        {models.map((model) => <ModelCard key={model.id} model={model} />)}
      </div>
      <div className="grid gap-4 lg:grid-cols-2">
        <ChartCard title="Total points by model"><LeaderboardBarChart data={leaderboard} /></ChartCard>
        <ChartCard title="Confidence by model"><ConfidenceChart data={leaderboard} /></ChartCard>
      </div>
      <LeaderboardTable data={leaderboard} />
    </div>
  );
}
