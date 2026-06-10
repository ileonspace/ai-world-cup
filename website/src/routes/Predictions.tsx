import { useEffect, useMemo, useState } from 'react';
import { PredictionsTable } from '../components/PredictionsTable';
import { api } from '../lib/api';
import type { Prediction } from '../lib/types';
import { unique } from '../lib/utils';

export function Predictions() {
  const [predictions, setPredictions] = useState<Prediction[]>([]);
  const [model, setModel] = useState('');
  const [query, setQuery] = useState('');
  useEffect(() => { void api.predictions().then(setPredictions); }, []);
  const models = unique(predictions.map((prediction) => prediction.model_name)).sort();
  const filtered = useMemo(
    () => predictions.filter((prediction) =>
      (!model || prediction.model_name === model) &&
      (!query || `${prediction.home_team} ${prediction.away_team} ${prediction.stage}`.toLowerCase().includes(query.toLowerCase()))
    ),
    [predictions, model, query]
  );
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Predictions</h1>
      <div className="flex flex-wrap gap-3">
        <select className="rounded-md border px-3 py-2 dark:border-slate-700 dark:bg-slate-950" value={model} onChange={(event) => setModel(event.target.value)}><option value="">All models</option>{models.map((item) => <option key={item}>{item}</option>)}</select>
        <input className="rounded-md border px-3 py-2 dark:border-slate-700 dark:bg-slate-950" placeholder="Search match, team, stage" value={query} onChange={(event) => setQuery(event.target.value)} />
      </div>
      <PredictionsTable predictions={filtered} />
    </div>
  );
}
