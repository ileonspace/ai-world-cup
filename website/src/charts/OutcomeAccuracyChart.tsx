import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import type { LeaderboardRow } from '../lib/types';

export function OutcomeAccuracyChart({ data }: { data: LeaderboardRow[] }) {
  return (
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="model_name" hide />
          <YAxis tickFormatter={(value) => `${Number(value) * 100}%`} />
          <Tooltip formatter={(value) => `${(Number(value) * 100).toFixed(1)}%`} />
          <Bar dataKey="outcome_accuracy" fill="#2563eb" name="Outcome accuracy" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
