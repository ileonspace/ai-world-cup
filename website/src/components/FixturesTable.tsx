import { Link } from 'react-router-dom';
import type { Fixture } from '../lib/types';
import { compactDate } from '../lib/utils';
import { EmptyState } from './EmptyState';

export function FixturesTable({ fixtures }: { fixtures: Fixture[] }) {
  if (!fixtures.length) return <EmptyState title="No fixtures exported" />;
  return (
    <div className="table-scroll rounded-lg border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-950">
      <table className="min-w-full text-left text-sm">
        <thead className="bg-slate-50 text-slate-600 dark:bg-slate-900 dark:text-slate-300">
          <tr>
            {['Match', 'Stage', 'Group', 'Teams', 'Kickoff', 'Venue', 'Status'].map((head) => (
              <th key={head} className="px-4 py-3 font-semibold">{head}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {fixtures.map((fixture) => (
            <tr key={`${fixture.match_number}-${fixture.home_team}`} className="border-t border-slate-100 dark:border-slate-800">
              <td className="px-4 py-3">
                {fixture.match_number ? <Link className="text-pitch hover:underline dark:text-emerald-300" to={`/matches/${fixture.match_number}`}>{fixture.match_number}</Link> : 'TBD'}
              </td>
              <td className="px-4 py-3">{fixture.stage ?? 'TBD'}</td>
              <td className="px-4 py-3">{fixture.group ?? '-'}</td>
              <td className="px-4 py-3">{fixture.home_team} vs {fixture.away_team}</td>
              <td className="px-4 py-3">{compactDate(fixture.kickoff_time)}</td>
              <td className="px-4 py-3">{fixture.venue ?? 'TBD'}</td>
              <td className="px-4 py-3">{fixture.status}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
