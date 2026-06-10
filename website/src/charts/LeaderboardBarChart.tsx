import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import type { LeaderboardRow } from '../lib/types';
import { EmptyState } from '../components/EmptyState';

export function LeaderboardBarChart({ data }: { data: LeaderboardRow[] }) {
  if (!data.length) return <EmptyState title="No leaderboard chart data" />;
  return (
    <div className="h-72">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data.slice(0, 12)}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="model_name" hide />
          <YAxis />
          <Tooltip />
          <Bar dataKey="total_points" fill="#0f5132" name="Total points" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
