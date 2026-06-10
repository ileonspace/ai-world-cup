import {
  flexRender,
  getCoreRowModel,
  getSortedRowModel,
  useReactTable,
  type ColumnDef,
  type SortingState
} from '@tanstack/react-table';
import { useState } from 'react';
import type { LeaderboardRow } from '../lib/types';
import { pct } from '../lib/utils';
import { EmptyState } from './EmptyState';

const columns: ColumnDef<LeaderboardRow>[] = [
  { header: 'Rank', accessorKey: 'rank' },
  { header: 'Model', accessorKey: 'model_name' },
  { header: 'Provider', accessorKey: 'provider' },
  { header: 'Points', accessorKey: 'total_points' },
  { header: 'Group', accessorKey: 'group_stage_points' },
  { header: 'Standings', accessorKey: 'group_standing_points' },
  { header: 'Knockout', accessorKey: 'knockout_points' },
  { header: 'Champion', accessorKey: 'champion_prediction' },
  { header: 'Outcome', cell: ({ row }) => pct(row.original.outcome_accuracy) },
  { header: 'Exact', cell: ({ row }) => pct(row.original.exact_score_accuracy) },
  { header: 'Confidence', cell: ({ row }) => row.original.average_confidence.toFixed(2) }
];

export function LeaderboardTable({ data }: { data: LeaderboardRow[] }) {
  const [sorting, setSorting] = useState<SortingState>([]);
  const table = useReactTable({
    data,
    columns,
    state: { sorting },
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel()
  });
  if (!data.length) return <EmptyState title="No leaderboard data" />;
  return (
    <div className="table-scroll rounded-lg border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-950">
      <table className="min-w-full text-left text-sm">
        <thead className="bg-slate-50 text-slate-600 dark:bg-slate-900 dark:text-slate-300">
          {table.getHeaderGroups().map((group) => (
            <tr key={group.id}>
              {group.headers.map((header) => (
                <th key={header.id} className="whitespace-nowrap px-4 py-3 font-semibold">
                  <button onClick={header.column.getToggleSortingHandler()}>
                    {flexRender(header.column.columnDef.header, header.getContext())}
                  </button>
                </th>
              ))}
            </tr>
          ))}
        </thead>
        <tbody>
          {table.getRowModel().rows.map((row) => (
            <tr key={row.id} className="border-t border-slate-100 dark:border-slate-800">
              {row.getVisibleCells().map((cell) => (
                <td key={cell.id} className="whitespace-nowrap px-4 py-3">
                  {flexRender(cell.column.columnDef.cell, cell.getContext())}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
