import type { Prediction } from '../lib/types';
import { EmptyState } from './EmptyState';

export function PredictionsTable({ predictions }: { predictions: Prediction[] }) {
  if (!predictions.length) return <EmptyState title="No predictions exported" />;
  return (
    <div className="table-scroll rounded-lg border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-950">
      <table className="min-w-full text-left text-sm">
        <thead className="bg-slate-50 text-slate-600 dark:bg-slate-900 dark:text-slate-300">
          <tr>
            {['Model', 'Match', 'Stage', 'Prediction', 'Winner', 'Confidence', 'Reasoning'].map((head) => (
              <th key={head} className="px-4 py-3 font-semibold">{head}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {predictions.map((prediction, index) => (
            <tr key={`${prediction.model_name}-${prediction.match_number}-${index}`} className="border-t border-slate-100 dark:border-slate-800">
              <td className="px-4 py-3">{prediction.model_name}</td>
              <td className="px-4 py-3">{prediction.match_number ?? '-'}</td>
              <td className="px-4 py-3">{prediction.stage}</td>
              <td className="px-4 py-3">{prediction.home_team} {prediction.predicted_home_goals}-{prediction.predicted_away_goals} {prediction.away_team}</td>
              <td className="px-4 py-3">{prediction.predicted_winner}</td>
              <td className="px-4 py-3">{prediction.confidence.toFixed(2)}</td>
              <td className="max-w-md px-4 py-3 text-slate-600 dark:text-slate-300">{prediction.reasoning_short}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
