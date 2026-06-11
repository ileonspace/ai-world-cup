import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { colorForIndex } from '../lib/palette';
import type { LeaderboardRow } from '../lib/types';

export function ExactScoreChart({ data }: { data: LeaderboardRow[] }) {
  return (
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ bottom: 48, left: 4, right: 8, top: 8 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="model_name" angle={-35} textAnchor="end" interval={0} height={70} tick={{ fontSize: 11 }} />
          <YAxis tickFormatter={(value) => `${Number(value) * 100}%`} />
          <Tooltip formatter={(value) => `${(Number(value) * 100).toFixed(1)}%`} />
          <Bar dataKey="exact_score_accuracy" name="Exact score accuracy">
            {data.map((row, index) => <Cell key={row.model_name} fill={colorForIndex(index)} />)}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
