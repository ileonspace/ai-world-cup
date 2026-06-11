import { Link } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { LeaderboardTable } from '../components/LeaderboardTable';
import { StatCard } from '../components/StatCard';
import { api } from '../lib/api';
import type { KnockoutPayload, LeaderboardRow, ProjectSummary } from '../lib/types';

export function Home() {
  const [summary, setSummary] = useState<ProjectSummary | null>(null);
  const [leaderboard, setLeaderboard] = useState<LeaderboardRow[]>([]);
  const [knockout, setKnockout] = useState<KnockoutPayload | null>(null);

  useEffect(() => {
    void Promise.all([api.summary(), api.leaderboard(), api.knockout()]).then(([s, l, k]) => {
      setSummary(s);
      setLeaderboard(l);
      setKnockout(k);
    });
  }, []);

  return (
    <div className="space-y-8">
      <section className="rounded-lg bg-pitch p-8 text-white shadow-sm dark:bg-emerald-900">
        <p className="text-sm font-semibold uppercase tracking-wide text-emerald-100">FIFA World Cup 2026 benchmark</p>
        <h1 className="mt-3 text-4xl font-bold tracking-tight md:text-6xl">AI World Cup</h1>
        <p className="mt-4 max-w-3xl text-lg text-emerald-50">
          A reproducible public benchmark for comparing LLM predictions using one shared full-tournament prompt.
        </p>
        <div className="mt-6 flex flex-wrap gap-3">
          <Link className="rounded-md bg-white px-4 py-2 font-semibold text-pitch" to="/leaderboard">Leaderboard</Link>
          <Link className="rounded-md border border-white/70 px-4 py-2 font-semibold text-white" to="/fixtures">Fixtures</Link>
          <Link className="rounded-md border border-white/70 px-4 py-2 font-semibold text-white" to="/methodology">Methodology</Link>
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-4">
        <StatCard label="Models compared" value={summary?.number_of_models ?? 0} />
        <StatCard label="Fixtures tracked" value={summary?.number_of_fixtures ?? 0} />
        <StatCard label="Predictions imported" value={summary?.number_of_predictions ?? 0} />
        <StatCard label="Latest snapshot" value={summary?.latest_data_snapshot_id ?? 'None'} detail={summary?.prompt_version} />
      </section>

      <section>
        <h2 className="mb-4 text-2xl font-semibold">Top leaderboard preview</h2>
        <LeaderboardTable data={leaderboard.slice(0, 5)} />
      </section>

      <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-950">
        <h2 className="text-2xl font-semibold">Champion predictions</h2>
        <div className="mt-4 grid gap-3 md:grid-cols-4">
          {(knockout?.champion_predictions ?? []).slice(0, 8).map((item) => (
            <div key={item.team} className="rounded-md bg-slate-50 p-4 dark:bg-slate-900">
              <div className="font-semibold">{item.team}</div>
              <div className="text-sm text-slate-500 dark:text-slate-400">{item.count} model picks</div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
