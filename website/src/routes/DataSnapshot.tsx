import { useEffect, useState } from 'react';
import { EmptyState } from '../components/EmptyState';
import { api } from '../lib/api';
import type { ProjectSummary, SnapshotInfo } from '../lib/types';
import { compactDate } from '../lib/utils';

export function DataSnapshot() {
  const [summary, setSummary] = useState<ProjectSummary | null>(null);
  const [snapshots, setSnapshots] = useState<SnapshotInfo[]>([]);
  useEffect(() => { void Promise.all([api.summary(), api.snapshots()]).then(([s, snaps]) => { setSummary(s); setSnapshots(snaps); }); }, []);
  if (!summary && !snapshots.length) return <EmptyState title="No snapshot data" />;
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Data snapshot</h1>
      <section className="rounded-lg border bg-white p-5 dark:border-slate-800 dark:bg-slate-950">
        <div className="grid gap-4 md:grid-cols-3">
          <div><div className="text-sm text-slate-500">Latest snapshot</div><div className="font-semibold">{summary?.latest_data_snapshot_id ?? 'None'}</div></div>
          <div><div className="text-sm text-slate-500">Prompt version</div><div className="font-semibold">{summary?.prompt_version ?? 'v1'}</div></div>
          <div><div className="text-sm text-slate-500">Last updated</div><div className="font-semibold">{compactDate(summary?.last_updated)}</div></div>
        </div>
      </section>
      <section className="rounded-lg border bg-white p-5 dark:border-slate-800 dark:bg-slate-950">
        <h2 className="text-xl font-semibold">Snapshots</h2>
        <div className="table-scroll mt-4">
          <table className="min-w-full text-left text-sm">
            <thead><tr>{['ID', 'Source', 'Created', 'Raw file', 'Prompt'].map((h) => <th className="px-3 py-2" key={h}>{h}</th>)}</tr></thead>
            <tbody>{snapshots.map((snapshot) => <tr className="border-t dark:border-slate-800" key={snapshot.data_snapshot_id}><td className="px-3 py-2">{snapshot.data_snapshot_id}</td><td className="px-3 py-2">{snapshot.source_name}</td><td className="px-3 py-2">{compactDate(snapshot.created_at)}</td><td className="px-3 py-2">{snapshot.raw_file_path}</td><td className="px-3 py-2">{snapshot.prompt_version}</td></tr>)}</tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
