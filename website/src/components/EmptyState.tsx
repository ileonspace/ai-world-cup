export function EmptyState({ title = 'No data yet', detail = 'Run aiwc site export to publish data.' }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-6 text-sm text-slate-600 shadow-sm dark:border-slate-800 dark:bg-slate-950 dark:text-slate-300">
      <div className="font-semibold text-slate-900 dark:text-white">{title}</div>
      <div className="mt-1">{detail}</div>
    </div>
  );
}
