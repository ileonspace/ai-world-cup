import { useEffect, useMemo, useState } from 'react';
import { EmptyState } from '../components/EmptyState';
import { api } from '../lib/api';
import type {
  TournamentBracketRound,
  TournamentGroupTable,
  TournamentSource,
  TournamentView,
  TournamentViewsPayload
} from '../lib/types';

const teamFlags: Record<string, string> = {
  Argentina: '🇦🇷',
  Algeria: '🇩🇿',
  Australia: '🇦🇺',
  Austria: '🇦🇹',
  Belgium: '🇧🇪',
  'Bosnia and Herzegovina': '🇧🇦',
  'Bosnia & Herzegovina': '🇧🇦',
  Brazil: '🇧🇷',
  Canada: '🇨🇦',
  'Cape Verde': '🇨🇻',
  Chile: '🇨🇱',
  Colombia: '🇨🇴',
  Croatia: '🇭🇷',
  Curaçao: '🇨🇼',
  Curacao: '🇨🇼',
  Denmark: '🇩🇰',
  'Democratic Republic of the Congo': '🇨🇩',
  'DR Congo': '🇨🇩',
  Ecuador: '🇪🇨',
  Egypt: '🇪🇬',
  England: '🏴',
  France: '🇫🇷',
  Germany: '🇩🇪',
  Ghana: '🇬🇭',
  Haiti: '🇭🇹',
  Iran: '🇮🇷',
  Iraq: '🇮🇶',
  Italy: '🇮🇹',
  'Ivory Coast': '🇨🇮',
  Japan: '🇯🇵',
  Jordan: '🇯🇴',
  Mexico: '🇲🇽',
  Morocco: '🇲🇦',
  Netherlands: '🇳🇱',
  'New Zealand': '🇳🇿',
  Norway: '🇳🇴',
  Panama: '🇵🇦',
  Paraguay: '🇵🇾',
  Portugal: '🇵🇹',
  Qatar: '🇶🇦',
  'Saudi Arabia': '🇸🇦',
  Scotland: '🏴',
  Senegal: '🇸🇳',
  'South Africa': '🇿🇦',
  'South Korea': '🇰🇷',
  Spain: '🇪🇸',
  Sweden: '🇸🇪',
  Switzerland: '🇨🇭',
  Tunisia: '🇹🇳',
  Turkey: '🇹🇷',
  'Czech Republic': '🇨🇿',
  Uzbekistan: '🇺🇿',
  Uruguay: '🇺🇾',
  USA: '🇺🇸',
  'United States': '🇺🇸',
  Wales: '🏴'
};

function flagFor(team: string): string {
  return teamFlags[team] ?? '';
}

function TeamName({ name }: { name: string }) {
  const flag = flagFor(name);
  return (
    <span className="inline-flex items-center gap-2">
      <span aria-hidden="true" className="w-5 text-center">
        {flag || name.slice(0, 1).toUpperCase()}
      </span>
      <span>{name}</span>
    </span>
  );
}

function SourceSelect({
  label,
  sources,
  value,
  onChange
}: {
  label: string;
  sources: TournamentSource[];
  value: string;
  onChange: (value: string) => void;
}) {
  return (
    <label className="flex flex-col gap-1 text-sm font-medium text-slate-700 dark:text-slate-200">
      {label}
      <select
        className="rounded-md border border-slate-300 bg-white px-3 py-2 text-slate-950 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-50"
        value={value}
        onChange={(event) => onChange(event.target.value)}
      >
        {!sources.length ? <option value="">No sources exported</option> : null}
        {value && !sources.some((source) => source.id === value) ? (
          <option value={value}>Select a source</option>
        ) : null}
        {sources.map((source) => (
          <option key={source.id} value={source.id}>
            {source.label}{source.provider ? ` (${source.provider})` : ''}
          </option>
        ))}
      </select>
    </label>
  );
}

function GroupTable({ table, compareTo }: { table: TournamentGroupTable; compareTo?: TournamentGroupTable }) {
  const compareRanks = new Map(compareTo?.rows.map((row) => [row.team, row.rank]) ?? []);
  return (
    <article className="rounded-lg border bg-white p-4 dark:border-slate-800 dark:bg-slate-950">
      <h3 className="text-base font-semibold">Group {table.group}</h3>
      <div className="table-scroll mt-3">
        <table className="min-w-full text-left text-xs">
          <thead className="text-slate-500 dark:text-slate-400">
            <tr>
              {['Rank', 'Team', 'MP', 'W', 'D', 'L', 'GF', 'GA', 'GD', 'Pts'].map((header) => (
                <th key={header} className="px-2 py-2 font-semibold">{header}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {table.rows.map((row) => {
              const otherRank = compareRanks.get(row.team);
              const rankMatches = otherRank === undefined || otherRank === row.rank;
              const qualified = row.rank <= 2;
              return (
                <tr
                  key={row.team}
                  className={`border-t dark:border-slate-800 ${
                    !rankMatches
                      ? 'bg-amber-50 dark:bg-amber-950/20'
                      : qualified
                        ? 'bg-emerald-50/70 dark:bg-emerald-950/20'
                        : ''
                  }`}
                >
                  <td className="px-2 py-2 font-semibold">{row.rank}</td>
                  <td className="min-w-36 px-2 py-2"><TeamName name={row.team} /></td>
                  <td className="px-2 py-2">{row.matches_played}</td>
                  <td className="px-2 py-2">{row.wins}</td>
                  <td className="px-2 py-2">{row.draws}</td>
                  <td className="px-2 py-2">{row.losses}</td>
                  <td className="px-2 py-2">{row.goals_for}</td>
                  <td className="px-2 py-2">{row.goals_against}</td>
                  <td className="px-2 py-2">{row.goal_difference}</td>
                  <td className="px-2 py-2 font-semibold">{row.points}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </article>
  );
}

function GroupSection({ primary, secondary }: { primary: TournamentView; secondary?: TournamentView }) {
  const secondaryByGroup = new Map(
    secondary?.group_tables.map((table) => [table.group, table]) ?? []
  );
  return (
    <section className="space-y-4">
      <div>
        <h2 className="text-2xl font-semibold">Group stage tables</h2>
        <p className="mt-1 text-sm text-slate-600 dark:text-slate-300">
          Tables are calculated from official results or each model's predicted group-stage scores.
        </p>
      </div>
      <div className={`grid gap-4 ${secondary ? '' : 'xl:grid-cols-2'}`}>
        {primary.group_tables.map((table) => (
          <div key={table.group} className={secondary ? 'grid gap-4 lg:grid-cols-2' : ''}>
            <GroupTable table={table} compareTo={secondaryByGroup.get(table.group)} />
            {secondary ? (
              <GroupTable
                table={secondaryByGroup.get(table.group) ?? { group: table.group, rows: [] }}
                compareTo={table}
              />
            ) : null}
          </div>
        ))}
      </div>
    </section>
  );
}

function MatchBox({ match }: { match: TournamentBracketRound['matches'][number] }) {
  const homeWinner = match.winner === match.home_team;
  const awayWinner = match.winner === match.away_team;
  return (
    <div className="rounded-md border border-slate-200 bg-slate-50 p-3 text-xs dark:border-slate-800 dark:bg-slate-900">
      <div className="mb-2 text-[11px] font-semibold text-slate-500 dark:text-slate-400">
        {match.match_number ? `Match ${match.match_number}` : 'Match TBD'}
      </div>
      <div className={`flex items-center justify-between gap-3 ${homeWinner ? 'font-bold text-pitch dark:text-emerald-300' : ''}`}>
        <TeamName name={match.home_team} />
        <span>{match.home_score ?? '-'}</span>
      </div>
      <div className={`mt-1 flex items-center justify-between gap-3 ${awayWinner ? 'font-bold text-pitch dark:text-emerald-300' : ''}`}>
        <TeamName name={match.away_team} />
        <span>{match.away_score ?? '-'}</span>
      </div>
    </div>
  );
}

function Bracket({ view }: { view: TournamentView }) {
  if (!view.knockout_rounds.length) {
    return <EmptyState title="No knockout bracket exported" />;
  }
  return (
    <div className="table-scroll">
      <div className="grid min-w-[1100px] grid-flow-col auto-cols-[220px] gap-4">
        {view.knockout_rounds.map((round) => (
          <section key={round.stage} className="space-y-3">
            <h3 className="sticky left-0 text-sm font-semibold text-slate-700 dark:text-slate-200">
              {round.stage}
            </h3>
            <div className="space-y-3">
              {round.matches.map((match, index) => (
                <MatchBox key={`${match.stage}-${match.match_number ?? index}`} match={match} />
              ))}
            </div>
          </section>
        ))}
      </div>
    </div>
  );
}

function BracketSection({ primary, secondary }: { primary: TournamentView; secondary?: TournamentView }) {
  return (
    <section className="space-y-4">
      <h2 className="text-2xl font-semibold">Knockout stage</h2>
      <div className={secondary ? 'grid gap-4 xl:grid-cols-2' : ''}>
        <article className="rounded-lg border bg-white p-4 dark:border-slate-800 dark:bg-slate-950">
          <h3 className="mb-4 text-lg font-semibold">{primary.source.label}</h3>
          <Bracket view={primary} />
        </article>
        {secondary ? (
          <article className="rounded-lg border bg-white p-4 dark:border-slate-800 dark:bg-slate-950">
            <h3 className="mb-4 text-lg font-semibold">{secondary.source.label}</h3>
            <Bracket view={secondary} />
          </article>
        ) : null}
      </div>
    </section>
  );
}

function FinalRanking({ view }: { view: TournamentView }) {
  if (!view.final_ranking && !view.awards) return null;
  return (
    <div className="space-y-4 rounded-lg border bg-white p-4 dark:border-slate-800 dark:bg-slate-950">
      {view.final_ranking ? (
        <div>
          <h3 className="text-lg font-semibold">{view.source.label} final four</h3>
          <dl className="mt-3 grid gap-3 text-sm sm:grid-cols-4">
            {[
              ['Champion', view.final_ranking.champion],
              ['Runner-up', view.final_ranking.runner_up],
              ['Third', view.final_ranking.third_place],
              ['Fourth', view.final_ranking.fourth_place]
            ].map(([label, team]) => (
              <div key={label} className="rounded-md bg-slate-50 p-3 dark:bg-slate-900">
                <dt className="text-slate-500 dark:text-slate-400">{label}</dt>
                <dd className="mt-1 font-semibold"><TeamName name={team} /></dd>
              </div>
            ))}
          </dl>
        </div>
      ) : null}
      {view.awards ? (
        <div>
          <h3 className="text-lg font-semibold">{view.source.label} awards</h3>
          <dl className="mt-3 grid gap-3 text-sm sm:grid-cols-4">
            {[
              ['Top scorer', view.awards.top_scorer],
              ['Best player', view.awards.best_player],
              ['Best young player', view.awards.best_young_player],
              ['Best goalkeeper', view.awards.best_goalkeeper]
            ].map(([label, person]) => (
              <div key={label} className="rounded-md bg-slate-50 p-3 dark:bg-slate-900">
                <dt className="text-slate-500 dark:text-slate-400">{label}</dt>
                <dd className="mt-1 font-semibold">{person || 'Not provided'}</dd>
              </div>
            ))}
          </dl>
        </div>
      ) : null}
    </div>
  );
}

export function TournamentExplorer() {
  const [payload, setPayload] = useState<TournamentViewsPayload | null>(null);
  const [primaryId, setPrimaryId] = useState('actual');
  const [secondaryId, setSecondaryId] = useState('');
  const [compare, setCompare] = useState(false);

  useEffect(() => {
    void api.tournamentViews().then((data) => {
      setPayload(data);
      const first = data.sources[0]?.id ?? 'actual';
      const second = data.sources.find((source) => source.id !== first)?.id ?? '';
      setPrimaryId(first);
      setSecondaryId(second);
    });
  }, []);

  const viewsById = useMemo(
    () => new Map(payload?.views.map((view) => [view.source.id, view]) ?? []),
    [payload]
  );
  const sources = payload?.sources ?? [];
  const primary = viewsById.get(primaryId);
  const secondary = compare && secondaryId !== primaryId ? viewsById.get(secondaryId) : undefined;

  if (!payload) return <EmptyState title="Loading tournament explorer" />;
  if (!sources.length || !primary) {
    return <EmptyState title="No tournament views exported" detail="Run aiwc site export to generate tournament_views.json." />;
  }

  return (
    <div className="space-y-8">
      <div className="rounded-lg bg-pitch p-6 text-white dark:bg-emerald-700">
        <p className="text-sm font-semibold uppercase tracking-wide text-emerald-100">Tournament Explorer</p>
        <h1 className="mt-2 text-3xl font-bold">Compare full World Cup paths</h1>
        <p className="mt-2 max-w-3xl text-sm text-emerald-50">
          Pick real results or any model submission, then inspect calculated group tables and
          predicted knockout brackets in one place.
        </p>
      </div>

      <section className="rounded-lg border bg-white p-4 dark:border-slate-800 dark:bg-slate-950">
        <div className="grid gap-4 md:grid-cols-[1fr_auto_1fr] md:items-end">
          <SourceSelect label="Primary view" sources={sources} value={primaryId} onChange={setPrimaryId} />
          <label className="flex items-center gap-2 rounded-md bg-slate-100 px-3 py-2 text-sm font-medium dark:bg-slate-900">
            <input
              checked={compare}
              className="h-4 w-4"
              type="checkbox"
              onChange={(event) => setCompare(event.target.checked)}
            />
            Compare
          </label>
          <SourceSelect
            label="Compare with"
            sources={sources.filter((source) => source.id !== primaryId)}
            value={secondaryId === primaryId ? '' : secondaryId}
            onChange={setSecondaryId}
          />
        </div>
      </section>

      <div className="grid gap-4 md:grid-cols-2">
        <FinalRanking view={primary} />
        {secondary ? <FinalRanking view={secondary} /> : null}
      </div>

      <GroupSection primary={primary} secondary={secondary} />
      <BracketSection primary={primary} secondary={secondary} />
    </div>
  );
}
