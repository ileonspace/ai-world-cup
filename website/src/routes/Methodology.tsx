export function Methodology() {
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

      <section className="rounded-lg border border-amber-200 bg-amber-50 p-5 text-amber-900 dark:border-amber-900 dark:bg-amber-950 dark:text-amber-100">
        <h2 className="font-semibold">Fairness note</h2>
        <p className="mt-2 text-sm">
          Search-enabled assistants should be compared separately unless every model is allowed to
          use live web search or external retrieval.
        </p>
      </section>
    </div>
  );
}
