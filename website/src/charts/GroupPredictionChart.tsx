import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import type { GroupsPayload } from '../lib/types';
import { EmptyState } from '../components/EmptyState';
import { colorForIndex } from '../lib/palette';

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
        <BarChart data={counts} margin={{ bottom: 48, left: 4, right: 8, top: 8 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="team" angle={-35} textAnchor="end" interval={0} height={70} tick={{ fontSize: 11 }} />
          <YAxis />
          <Tooltip />
          <Bar dataKey="count" name="Group winner picks">
            {counts.map((row, index) => <Cell key={row.team} fill={colorForIndex(index)} />)}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
