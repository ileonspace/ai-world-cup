import { useEffect, useMemo, useState } from 'react';
import { FixturesTable } from '../components/FixturesTable';
import { api } from '../lib/api';
import type { Fixture } from '../lib/types';
import { unique } from '../lib/utils';

export function Fixtures() {
  const [fixtures, setFixtures] = useState<Fixture[]>([]);
  const [stage, setStage] = useState('');
  const [team, setTeam] = useState('');
  const [status, setStatus] = useState('');
  useEffect(() => { void api.fixtures().then(setFixtures); }, []);
  const teams = unique(fixtures.flatMap((fixture) => [fixture.home_team, fixture.away_team])).sort();
  const stages = unique(fixtures.map((fixture) => fixture.stage ?? 'TBD')).sort();
  const statuses = unique(fixtures.map((fixture) => fixture.status)).sort();
  const filtered = useMemo(
    () => fixtures.filter((fixture) =>
      (!stage || fixture.stage === stage) &&
      (!team || fixture.home_team === team || fixture.away_team === team) &&
      (!status || fixture.status === status)
    ),
    [fixtures, stage, team, status]
  );
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Fixtures</h1>
      <div className="flex flex-wrap gap-3">
        <select className="rounded-md border px-3 py-2 dark:border-slate-700 dark:bg-slate-950" value={stage} onChange={(event) => setStage(event.target.value)}><option value="">All stages</option>{stages.map((item) => <option key={item}>{item}</option>)}</select>
        <select className="rounded-md border px-3 py-2 dark:border-slate-700 dark:bg-slate-950" value={team} onChange={(event) => setTeam(event.target.value)}><option value="">All teams</option>{teams.map((item) => <option key={item}>{item}</option>)}</select>
        <select className="rounded-md border px-3 py-2 dark:border-slate-700 dark:bg-slate-950" value={status} onChange={(event) => setStatus(event.target.value)}><option value="">All statuses</option>{statuses.map((item) => <option key={item}>{item}</option>)}</select>
      </div>
      <FixturesTable fixtures={filtered} />
    </div>
  );
}
