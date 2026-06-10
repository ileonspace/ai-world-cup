import { useEffect, useMemo, useState } from 'react';
import { useParams } from 'react-router-dom';
import { Pie, PieChart, ResponsiveContainer, Tooltip, Cell } from 'recharts';
import { ChartCard } from '../components/ChartCard';
import { EmptyState } from '../components/EmptyState';
import { PredictionsTable } from '../components/PredictionsTable';
import { api } from '../lib/api';
import type { Fixture, Prediction } from '../lib/types';
import { compactDate } from '../lib/utils';

const colors = ['#0f5132', '#2563eb', '#d8a31a'];

export function MatchDetails() {
  const { matchNumber } = useParams();
  const number = Number(matchNumber);
  const [fixtures, setFixtures] = useState<Fixture[]>([]);
  const [predictions, setPredictions] = useState<Prediction[]>([]);
  useEffect(() => {
    void Promise.all([api.fixtures(), api.predictions()]).then(([f, p]) => {
      setFixtures(f);
      setPredictions(p);
    });
  }, []);
  const fixture = fixtures.find((item) => item.match_number === number);
  const matchPredictions = predictions.filter((item) => item.match_number === number);
  const distribution = useMemo(() => {
    const counts = matchPredictions.reduce<Record<string, number>>((acc, item) => {
      acc[item.predicted_outcome] = (acc[item.predicted_outcome] ?? 0) + 1;
      return acc;
    }, {});
    return Object.entries(counts).map(([name, value]) => ({ name, value }));
  }, [matchPredictions]);
  if (!fixture) return <EmptyState title="Match not found" detail="This match number is not in exported fixtures." />;
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Match {fixture.match_number}</h1>
        <p className="mt-2 text-slate-600 dark:text-slate-300">{fixture.home_team} vs {fixture.away_team}</p>
      </div>
      <section className="grid gap-4 md:grid-cols-4">
        <div className="rounded-lg border bg-white p-4 dark:border-slate-800 dark:bg-slate-950"><div className="text-sm text-slate-500">Stage</div><div className="font-semibold">{fixture.stage}</div></div>
        <div className="rounded-lg border bg-white p-4 dark:border-slate-800 dark:bg-slate-950"><div className="text-sm text-slate-500">Kickoff</div><div className="font-semibold">{compactDate(fixture.kickoff_time)}</div></div>
        <div className="rounded-lg border bg-white p-4 dark:border-slate-800 dark:bg-slate-950"><div className="text-sm text-slate-500">Venue</div><div className="font-semibold">{fixture.venue ?? 'TBD'}</div></div>
        <div className="rounded-lg border bg-white p-4 dark:border-slate-800 dark:bg-slate-950"><div className="text-sm text-slate-500">Result</div><div className="font-semibold">{fixture.home_score ?? '-'} - {fixture.away_score ?? '-'}</div></div>
      </section>
      <ChartCard title="Predicted outcome distribution">
        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie data={distribution} dataKey="value" nameKey="name" label>
                {distribution.map((_, index) => <Cell key={index} fill={colors[index % colors.length]} />)}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </ChartCard>
      <PredictionsTable predictions={matchPredictions} />
    </div>
  );
}
