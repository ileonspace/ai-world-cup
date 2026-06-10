export function StatCard({ label, value, detail }: { label: string; value: string | number; detail?: string }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-950">
      <div className="text-sm text-slate-500 dark:text-slate-400">{label}</div>
      <div className="mt-2 text-3xl font-semibold text-slate-950 dark:text-white">{value}</div>
      {detail ? <div className="mt-2 text-sm text-slate-500 dark:text-slate-400">{detail}</div> : null}
    </div>
  );
}
