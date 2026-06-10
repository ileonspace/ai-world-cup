import { useEffect, useState } from 'react';
import { EmptyState } from '../components/EmptyState';
import { api } from '../lib/api';
import type { KnockoutPayload } from '../lib/types';

export function Knockout() {
  const [data, setData] = useState<KnockoutPayload | null>(null);
  useEffect(() => { void api.knockout().then(setData); }, []);
  if (!data) return <EmptyState title="Loading knockout data" />;
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Knockout predictions</h1>
      <section className="grid gap-4 md:grid-cols-4">
        {data.champion_predictions.slice(0, 8).map((item) => (
          <div key={item.team} className="rounded-lg border bg-white p-5 dark:border-slate-800 dark:bg-slate-950">
            <div className="text-sm text-slate-500">Champion picks</div>
            <div className="mt-2 text-xl font-semibold">{item.team}</div>
            <div className="text-sm text-slate-500">{item.count} models</div>
          </div>
        ))}
      </section>
      <section className="rounded-lg border bg-white p-5 dark:border-slate-800 dark:bg-slate-950">
        <h2 className="text-xl font-semibold">Final rankings by model</h2>
        <div className="table-scroll mt-4">
          <table className="min-w-full text-left text-sm">
            <thead><tr>{['Model', 'Champion', 'Runner-up', 'Third', 'Fourth'].map((h) => <th className="px-3 py-2" key={h}>{h}</th>)}</tr></thead>
            <tbody>{data.final_ranking_predictions.map((row) => <tr className="border-t dark:border-slate-800" key={row.model_name}><td className="px-3 py-2">{row.model_name}</td><td className="px-3 py-2">{row.champion}</td><td className="px-3 py-2">{row.runner_up}</td><td className="px-3 py-2">{row.third_place}</td><td className="px-3 py-2">{row.fourth_place}</td></tr>)}</tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
