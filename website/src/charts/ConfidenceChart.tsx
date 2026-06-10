import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import type { LeaderboardRow } from '../lib/types';

export function ConfidenceChart({ data }: { data: LeaderboardRow[] }) {
  return (
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="model_name" hide />
          <YAxis domain={[0, 1]} />
          <Tooltip />
          <Bar dataKey="average_confidence" fill="#7c3aed" name="Average confidence" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
