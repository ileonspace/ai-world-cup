import type { ModelInfo } from '../lib/types';

export function ModelCard({ model }: { model: ModelInfo }) {
  return (
    <article className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-950">
      <div className="text-lg font-semibold text-slate-950 dark:text-white">{model.model_display_name}</div>
      <div className="mt-1 text-sm text-slate-500 dark:text-slate-400">{model.provider}</div>
      <div className="mt-4 text-sm">
        <span className="rounded-md bg-emerald-50 px-2 py-1 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300">
          {model.access_mode}
        </span>
      </div>
      <div className="mt-3 text-sm text-slate-500 dark:text-slate-400">
        Submitted: {model.submitted_at ? new Date(model.submitted_at).toLocaleDateString() : 'Not submitted'}
      </div>
    </article>
  );
}
