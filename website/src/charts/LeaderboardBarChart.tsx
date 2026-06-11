import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { EmptyState } from '../components/EmptyState';
import { colorForIndex } from '../lib/palette';
import type { LeaderboardRow } from '../lib/types';

export function LeaderboardBarChart({ data }: { data: LeaderboardRow[] }) {
  if (!data.length) return <EmptyState title="No leaderboard chart data" />;
  return (
    <div className="h-72">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data.slice(0, 12)} margin={{ bottom: 48, left: 4, right: 8, top: 8 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="model_name" angle={-35} textAnchor="end" interval={0} height={70} tick={{ fontSize: 11 }} />
          <YAxis />
          <Tooltip />
          <Bar dataKey="total_points" name="Total points">
            {data.slice(0, 12).map((row, index) => <Cell key={row.model_name} fill={colorForIndex(index)} />)}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
