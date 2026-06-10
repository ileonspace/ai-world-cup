import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import type { GroupsPayload } from '../lib/types';
import { EmptyState } from '../components/EmptyState';

export function GroupPredictionChart({ data }: { data: GroupsPayload }) {
  const winners = data.predicted_group_standings.filter((row) => row.rank === 1);
  const counts = Object.entries(
    winners.reduce<Record<string, number>>((acc, row) => {
      acc[row.team] = (acc[row.team] ?? 0) + 1;
      return acc;
    }, {})
  )
    .map(([team, count]) => ({ team, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 12);
  if (!counts.length) return <EmptyState title="No group prediction data" />;
  return (
    <div className="h-72">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={counts}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="team" hide />
          <YAxis />
          <Tooltip />
          <Bar dataKey="count" fill="#0f5132" name="Group winner picks" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
