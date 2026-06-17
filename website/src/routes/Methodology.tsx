import { useEffect, useState } from 'react';
import { ModelCard } from '../components/ModelCard';
import { api } from '../lib/api';
import type { ModelInfo } from '../lib/types';

const scoringSections = [
  {
    title: 'Match prediction scoring',
    rows: [
      ['Exact score', '5'],
      ['Correct outcome', '3'],
      ['Correct winner', '2'],
      ['Correct goal difference', '1']
    ],
    note: 'For draws, winner points are not awarded separately because the draw is already represented by the correct outcome.'
  },
  {
    title: 'Group standing scoring',
    rows: [
      ['Correct group winner', '5'],
      ['Correct top two teams', '5'],
      ['Correct qualified team from group', '3 per team'],
      ['Exact team rank', '2 per team']
    ]
  },
  {
    title: 'Knockout and tournament scoring',
    rows: [
      ['Correct team reaches Round of 32', '2'],
      ['Correct team reaches Round of 16', '4'],
      ['Correct team reaches quarter-final', '6'],
      ['Correct team reaches semi-final', '8'],
      ['Correct finalist', '12'],
      ['Correct champion', '20'],
      ['Correct runner-up', '10'],
      ['Correct third place', '8'],
      ['Correct fourth place', '5']
    ],
    note: 'Total tournament points are the sum of all applicable scoring components.'
  }
];

export function Methodology() {
  const [models, setModels] = useState<ModelInfo[]>([]);

  useEffect(() => { void api.models().then(setModels); }, []);

  return (
    <div className="space-y-8">
      <section>
        <p className="text-sm font-semibold uppercase tracking-wide text-emerald-700 dark:text-emerald-300">
          Benchmark design
        </p>
        <h1 className="mt-2 text-3xl font-bold">Methodology</h1>
        <p className="mt-3 max-w-3xl text-slate-600 dark:text-slate-300">
          AI World Cup compares model forecasts under controlled conditions: same prompt, same
          fixture context, same data snapshot, same JSON schema, and the same scoring rules.
        </p>
      </section>

      <section className="grid gap-4 md:grid-cols-3">
        {[
          ['Same data', 'Every model receives the same exported World Cup fixtures, groups, venues, and tournament structure.'],
          ['Manual submission', 'The repository does not call LLM APIs. Responses are copied back into the project exactly as returned.'],
          ['Static publishing', 'The CLI exports website-ready JSON, so GitHub Pages can show results without Python or SQLite.']
        ].map(([title, text]) => (
          <article key={title} className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-950">
            <h2 className="text-lg font-semibold">{title}</h2>
            <p className="mt-2 text-sm text-slate-600 dark:text-slate-300">{text}</p>
          </article>
        ))}
      </section>

      <section className="space-y-4">
        <div>
          <h2 className="text-2xl font-semibold">Models compared</h2>
          <p className="mt-2 max-w-3xl text-slate-600 dark:text-slate-300">
            These are the submitted model runs included in the current exported benchmark data.
            Search-enabled models should be interpreted separately unless every model has the same
            retrieval access.
          </p>
        </div>
        <div className="grid gap-4 md:grid-cols-3">
          {models.map((model) => <ModelCard key={model.id} model={model} />)}
        </div>
      </section>

      <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-950">
        <h2 className="text-xl font-semibold">Manual LLM submission protocol</h2>
        <ol className="mt-4 list-decimal space-y-2 pl-5 text-slate-600 dark:text-slate-300">
          <li>Generate the tournament prompt from the repository.</li>
          <li>Copy the full prompt without edits.</li>
          <li>Send the exact same prompt to each model.</li>
          <li>Save each raw answer exactly as returned.</li>
          <li>Import the response with the CLI.</li>
          <li>Keep prompt version and data snapshot fixed for fair comparison.</li>
        </ol>
      </section>

      <section className="grid gap-4 lg:grid-cols-2">
        <article className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-950">
          <h2 className="text-xl font-semibold">Validation</h2>
          <p className="mt-3 text-slate-600 dark:text-slate-300">
            Imported JSON is parsed, normalized for common formatting drift, and checked for match
            coverage, score/outcome consistency, confidence ranges, knockout winners, and group
            standing consistency. Warnings remain visible without discarding usable predictions.
          </p>
        </article>
        <article className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-950">
          <h2 className="text-xl font-semibold">Scoring</h2>
          <p className="mt-3 text-slate-600 dark:text-slate-300">
            Scores update gradually as real results become available. The system rewards exact
            scores, outcomes, winners, goal difference, group standings, knockout progression, and
            final ranking predictions.
          </p>
        </article>
      </section>

      <section className="space-y-4">
        <div>
          <h2 className="text-2xl font-semibold">How points are calculated</h2>
          <p className="mt-2 max-w-3xl text-slate-600 dark:text-slate-300">
            Scores update as real results become available. Each model's leaderboard total is the
            sum of match-level, group-standing, knockout, and final-ranking points.
          </p>
        </div>
        <div className="grid gap-4 lg:grid-cols-3">
          {scoringSections.map((section) => (
            <article key={section.title} className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-950">
              <h3 className="text-lg font-semibold">{section.title}</h3>
              <div className="table-scroll mt-4">
                <table className="min-w-full text-left text-sm">
                  <thead className="text-slate-500 dark:text-slate-400">
                    <tr>
                      <th className="pb-2 font-semibold">Prediction type</th>
                      <th className="pb-2 text-right font-semibold">Points</th>
                    </tr>
                  </thead>
                  <tbody>
                    {section.rows.map(([label, points]) => (
                      <tr key={label} className="border-t border-slate-100 dark:border-slate-800">
                        <td className="py-2 pr-3">{label}</td>
                        <td className="py-2 text-right font-semibold">{points}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              {section.note ? (
                <p className="mt-3 text-xs text-slate-500 dark:text-slate-400">{section.note}</p>
              ) : null}
            </article>
          ))}
        </div>
      </section>

      <section className="rounded-lg border border-amber-200 bg-amber-50 p-5 text-amber-900 dark:border-amber-900 dark:bg-amber-950 dark:text-amber-100">
        <h2 className="font-semibold">Fairness note</h2>
        <p className="mt-2 text-sm">
          Search-enabled assistants should be compared separately unless every model is allowed to
          use live web search or external retrieval.
        </p>
      </section>

      <section className="rounded-lg border border-emerald-200 bg-emerald-50 p-5 dark:border-emerald-900 dark:bg-emerald-950">
        <h2 className="font-semibold">Repository and reproducibility</h2>
        <p className="mt-2 text-sm text-slate-700 dark:text-slate-200">
          The benchmark is designed to be auditable: prompts, response files, validation logic,
          scoring rules, exported website JSON, and deployment configuration are all kept in the
          repository.
        </p>
        <a
          className="mt-4 inline-flex rounded-md bg-pitch px-4 py-2 text-sm font-semibold text-white dark:bg-emerald-500 dark:text-slate-950"
          href="https://github.com/jonaidshianifar/ai-world-cup/"
          rel="noreferrer"
          target="_blank"
        >
          View GitHub repository
        </a>
      </section>
    </div>
  );
}
