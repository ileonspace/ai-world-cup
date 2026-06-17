import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { EmptyState } from '../components/EmptyState';
import { api } from '../lib/api';
import type { Fixture, Prediction } from '../lib/types';
import { unique } from '../lib/utils';

type MatchPredictionGroup = {
  key: string;
  matchNumber: number | null;
  stage: string;
  group: string | null;
  homeTeam: string;
  awayTeam: string;
  status: string | null;
  homeScore: number | null;
  awayScore: number | null;
  winner: string | null;
  predictions: Prediction[];
};

function stageLabel(value: string | null | undefined): string {
  if (!value) return 'TBD';
  if (value.toLowerCase() === 'group') return 'Group Stage';
  return value;
}

function isGroupStage(value: string | null | undefined): boolean {
  return stageLabel(value).toLowerCase().includes('group');
}

function matchKey(matchNumber: number | null | undefined, homeTeam: string, awayTeam: string, stage: string | null | undefined): string {
  return matchNumber ? `match-${matchNumber}` : `${stage ?? 'stage'}-${homeTeam}-${awayTeam}`;
}

function resultWinner(group: MatchPredictionGroup): string | null {
  if (group.winner) return group.winner;
  if (group.homeScore === null || group.awayScore === null) return null;
  if (group.homeScore === group.awayScore) return 'Draw';
  return group.homeScore > group.awayScore ? group.homeTeam : group.awayTeam;
}

function predictionWinner(prediction: Prediction): string {
  if (prediction.predicted_home_goals === prediction.predicted_away_goals) return 'Draw';
  return prediction.predicted_winner;
}

function predictionMatchesResult(prediction: Prediction, group: MatchPredictionGroup): boolean {
  const winner = resultWinner(group);
  if (!winner) return false;
  return winner === predictionWinner(prediction);
}

const roundOrder = ['Round of 32', 'Round of 16', 'Quarter-final', 'Semi-final', 'Third Place', 'Third-place match', 'Final'];

export function Predictions() {
  const [predictions, setPredictions] = useState<Prediction[]>([]);
  const [fixtures, setFixtures] = useState<Fixture[]>([]);
  const [phase, setPhase] = useState('');
  const [group, setGroup] = useState('');
  const [round, setRound] = useState('');
  const [team, setTeam] = useState('');
  const [model, setModel] = useState('');
  const [query, setQuery] = useState('');

  useEffect(() => {
    void Promise.all([api.predictions(), api.fixtures()]).then(([predictionRows, fixtureRows]) => {
      setPredictions(predictionRows);
      setFixtures(fixtureRows);
    });
  }, []);

  const models = unique(predictions.map((prediction) => prediction.model_name)).sort();
  const teams = unique([
    ...fixtures.flatMap((fixture) => [fixture.home_team, fixture.away_team]),
    ...predictions.flatMap((prediction) => [prediction.home_team, prediction.away_team])
  ]).sort();

  const fixtureByKey = useMemo(
    () => new Map(fixtures.map((fixture) => [
      matchKey(fixture.match_number, fixture.home_team, fixture.away_team, fixture.stage),
      fixture
    ])),
    [fixtures]
  );

  const predictionGroups = useMemo(() => {
    const grouped = new Map<string, MatchPredictionGroup>();
    predictions.forEach((prediction) => {
      const key = matchKey(prediction.match_number, prediction.home_team, prediction.away_team, prediction.stage);
      const fixture = fixtureByKey.get(key);
      const existing = grouped.get(key);
      if (existing) {
        existing.predictions.push(prediction);
        return;
      }
      grouped.set(key, {
        key,
        matchNumber: prediction.match_number,
        stage: stageLabel(fixture?.stage ?? prediction.stage),
        group: fixture?.group ?? null,
        homeTeam: fixture?.home_team ?? prediction.home_team,
        awayTeam: fixture?.away_team ?? prediction.away_team,
        status: fixture?.status ?? null,
        homeScore: fixture?.home_score ?? null,
        awayScore: fixture?.away_score ?? null,
        winner: fixture?.winner ?? null,
        predictions: [prediction]
      });
    });
    return Array.from(grouped.values()).sort((a, b) => {
      if (a.matchNumber === null && b.matchNumber === null) return a.stage.localeCompare(b.stage);
      if (a.matchNumber === null) return 1;
      if (b.matchNumber === null) return -1;
      return a.matchNumber - b.matchNumber;
    });
  }, [fixtureByKey, predictions]);

  const groups = unique(predictionGroups.map((item) => item.group).filter((item): item is string => Boolean(item))).sort();
  const rounds = unique(predictionGroups.filter((item) => !isGroupStage(item.stage)).map((item) => item.stage))
    .sort((a, b) => {
      const aIndex = roundOrder.indexOf(a);
      const bIndex = roundOrder.indexOf(b);
      if (aIndex === -1 && bIndex === -1) return a.localeCompare(b);
      if (aIndex === -1) return 1;
      if (bIndex === -1) return -1;
      return aIndex - bIndex;
    });

  const filtered = useMemo(() => {
    const queryValue = query.toLowerCase();
    return predictionGroups
      .map((item) => ({
        ...item,
        predictions: item.predictions.filter((prediction) => !model || prediction.model_name === model)
      }))
      .filter((item) => {
        const inGroupStage = isGroupStage(item.stage);
        return (
          item.predictions.length > 0 &&
          (!phase || (phase === 'group' ? inGroupStage : !inGroupStage)) &&
          (!group || item.group === group) &&
          (!round || item.stage === round) &&
          (!team || item.homeTeam === team || item.awayTeam === team) &&
          (!queryValue || `${item.homeTeam} ${item.awayTeam} ${item.stage} ${item.group ?? ''}`.toLowerCase().includes(queryValue))
        );
      });
  }, [group, model, phase, predictionGroups, query, round, team]);

  const filterClass = 'rounded-md border border-slate-300 bg-white px-3 py-2 dark:border-slate-700 dark:bg-slate-950';

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Predictions</h1>
        <p className="mt-2 text-slate-600 dark:text-slate-300">One box per match, with the real result beside every model prediction.</p>
      </div>
      <div className="flex flex-wrap gap-3">
        <select className={filterClass} value={phase} onChange={(event) => { setPhase(event.target.value); setGroup(''); setRound(''); }}>
          <option value="">All phases</option>
          <option value="group">Group stage</option>
          <option value="knockout">Knockout</option>
        </select>
        {phase === 'group' ? (
          <select className={filterClass} value={group} onChange={(event) => setGroup(event.target.value)}>
            <option value="">All groups</option>
            {groups.map((item) => <option key={item} value={item}>Group {item}</option>)}
          </select>
        ) : null}
        {phase === 'knockout' ? (
          <select className={filterClass} value={round} onChange={(event) => setRound(event.target.value)}>
            <option value="">All rounds</option>
            {rounds.map((item) => <option key={item}>{item}</option>)}
          </select>
        ) : null}
        <select className={filterClass} value={team} onChange={(event) => setTeam(event.target.value)}>
          <option value="">All teams</option>
          {teams.map((item) => <option key={item}>{item}</option>)}
        </select>
        <select className={filterClass} value={model} onChange={(event) => setModel(event.target.value)}>
          <option value="">All models</option>
          {models.map((item) => <option key={item}>{item}</option>)}
        </select>
        <input className={filterClass} placeholder="Search match, team, stage" value={query} onChange={(event) => setQuery(event.target.value)} />
      </div>
      {!filtered.length ? (
        <EmptyState title="No matching predictions" detail="Try changing the phase, group, round, team, or model filter." />
      ) : (
        <div className="grid gap-4">
          {filtered.map((item) => {
            const hasResult = item.homeScore !== null && item.awayScore !== null;
            const actualWinner = resultWinner(item);
            return (
              <article key={item.key} className="rounded-lg border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-950">
                <div className="flex flex-wrap items-start justify-between gap-4 border-b border-slate-100 p-4 dark:border-slate-800">
                  <div>
                    <div className="text-sm font-semibold text-slate-500 dark:text-slate-400">
                      {item.matchNumber ? (
                        <Link className="text-pitch hover:underline dark:text-emerald-300" to={`/matches/${item.matchNumber}`}>Match {item.matchNumber}</Link>
                      ) : 'Match TBD'} · {item.stage}{item.group ? ` · Group ${item.group}` : ''}
                    </div>
                    <h2 className="mt-1 text-xl font-bold">{item.homeTeam} vs {item.awayTeam}</h2>
                  </div>
                  <div className="min-w-48 rounded-md bg-slate-50 px-4 py-3 text-sm dark:bg-slate-900">
                    <div className="text-slate-500 dark:text-slate-400">Real result</div>
                    <div className="text-lg font-bold">
                      {hasResult ? `${item.homeTeam} ${item.homeScore}-${item.awayScore} ${item.awayTeam}` : 'Pending'}
                    </div>
                    <div className="text-xs text-slate-500 dark:text-slate-400">
                      {actualWinner ? `Winner: ${actualWinner}` : item.status ?? 'No result exported'}
                    </div>
                  </div>
                </div>
                <div className="table-scroll">
                  <table className="min-w-full text-left text-sm">
                    <thead className="bg-slate-50 text-slate-600 dark:bg-slate-900 dark:text-slate-300">
                      <tr>
                        {['Model', 'Prediction', 'Winner', 'Confidence', 'Points', 'Reasoning'].map((head) => (
                          <th key={head} className="px-4 py-3 font-semibold">{head}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {item.predictions.map((prediction) => {
                        const matchesResult = predictionMatchesResult(prediction, item);
                        return (
                          <tr key={`${prediction.model_name}-${prediction.match_number ?? prediction.stage}-${prediction.home_team}-${prediction.away_team}`} className="border-t border-slate-100 dark:border-slate-800">
                            <td className="px-4 py-3 font-semibold">{prediction.model_name}</td>
                            <td className="px-4 py-3">{prediction.home_team} {prediction.predicted_home_goals}-{prediction.predicted_away_goals} {prediction.away_team}</td>
                            <td className="px-4 py-3">
                              <span className={`rounded-full px-2 py-1 text-xs font-semibold ${matchesResult ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-200' : 'bg-slate-100 text-slate-700 dark:bg-slate-900 dark:text-slate-300'}`}>
                                {predictionWinner(prediction)}
                              </span>
                            </td>
                            <td className="px-4 py-3">{prediction.confidence.toFixed(2)}</td>
                            <td className="px-4 py-3">{prediction.points ?? '-'}</td>
                            <td className="max-w-xl px-4 py-3 text-slate-600 dark:text-slate-300">{prediction.reasoning_short}</td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </article>
            );
          })}
        </div>
      )}
    </div>
  );
}
