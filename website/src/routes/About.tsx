export function About() {
  return (
    <div className="space-y-8">
      <section>
        <p className="text-sm font-semibold uppercase tracking-wide text-emerald-700 dark:text-emerald-300">
          Project overview
        </p>
        <h1 className="mt-2 text-3xl font-bold">About AI World Cup</h1>
        <p className="mt-3 max-w-3xl text-slate-600 dark:text-slate-300">
          AI World Cup is a public experiment for comparing how different language models forecast
          FIFA World Cup 2026 when they all receive one identical full-tournament prompt.
        </p>
      </section>

      <section className="grid gap-4 md:grid-cols-2">
        <article className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-950">
          <h2 className="text-xl font-semibold">Motivation</h2>
          <p className="mt-3 text-slate-600 dark:text-slate-300">
            Forecasting football requires reasoning under uncertainty. This project makes model
            predictions comparable by fixing the data, prompt, schema, and scoring rules.
          </p>
        </article>
        <article className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-950">
          <h2 className="text-xl font-semibold">How it works</h2>
          <p className="mt-3 text-slate-600 dark:text-slate-300">
            The Python CLI syncs football data, generates the prompt, imports manual responses,
            validates JSON, evaluates predictions, and exports static website data.
          </p>
        </article>
        <article className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-950">
          <h2 className="text-xl font-semibold">What is public</h2>
          <p className="mt-3 text-slate-600 dark:text-slate-300">
            The website shows fixtures, model predictions, confidence, reasoning snippets, champion
            picks, group forecasts, snapshots, and leaderboard tables.
          </p>
        </article>
        <article className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-950">
          <h2 className="text-xl font-semibold">Limitations</h2>
          <p className="mt-3 text-slate-600 dark:text-slate-300">
            Model versions can change, football data sources can be incomplete, and some assistants
            may use hidden tools. The benchmark records warnings rather than hiding uncertainty.
          </p>
        </article>
      </section>

      <section className="rounded-lg border border-red-200 bg-red-50 p-5 text-red-900 dark:border-red-900 dark:bg-red-950 dark:text-red-100">
        <h2 className="font-semibold">Not betting advice</h2>
        <p className="mt-2 text-sm">
          AI World Cup is for research, benchmarking, and visualization. It is not betting advice,
          financial advice, or a guarantee of any real-world result.
        </p>
      </section>
    </div>
  );
}
