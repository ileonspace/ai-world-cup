import { useEffect, useState } from 'react';
import { ChartCard } from '../components/ChartCard';
import { EmptyState } from '../components/EmptyState';
import { GroupPredictionChart } from '../charts/GroupPredictionChart';
import { api } from '../lib/api';
import type { GroupsPayload } from '../lib/types';

export function Groups() {
  const [groups, setGroups] = useState<GroupsPayload | null>(null);
  useEffect(() => { void api.groups().then(setGroups); }, []);
  if (!groups) return <EmptyState title="Loading groups" />;
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Groups</h1>
      <ChartCard title="Most picked group winners"><GroupPredictionChart data={groups} /></ChartCard>
      <section className="grid gap-4 md:grid-cols-3">
        {groups.official_groups.map((group) => (
          <article key={group.group} className="rounded-lg border bg-white p-5 dark:border-slate-800 dark:bg-slate-950">
            <h2 className="text-lg font-semibold">Group {group.group}</h2>
            <ul className="mt-3 space-y-2 text-sm text-slate-600 dark:text-slate-300">
              {group.teams.map((team) => <li key={team}>{team}</li>)}
            </ul>
          </article>
        ))}
      </section>
      <section className="rounded-lg border bg-white p-5 dark:border-slate-800 dark:bg-slate-950">
        <h2 className="text-xl font-semibold">Predicted standings</h2>
        <div className="table-scroll mt-4">
          <table className="min-w-full text-left text-sm">
            <thead><tr>{['Model', 'Group', 'Rank', 'Team', 'Pts', 'GD'].map((h) => <th className="px-3 py-2" key={h}>{h}</th>)}</tr></thead>
            <tbody>{groups.predicted_group_standings.map((row, index) => <tr className="border-t dark:border-slate-800" key={index}><td className="px-3 py-2">{row.model_name}</td><td className="px-3 py-2">{row.group}</td><td className="px-3 py-2">{row.rank}</td><td className="px-3 py-2">{row.team}</td><td className="px-3 py-2">{row.points}</td><td className="px-3 py-2">{row.goal_difference}</td></tr>)}</tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
