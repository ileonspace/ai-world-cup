export function Footer() {
  return (
    <footer className="mt-12 border-t border-slate-200 py-8 text-sm text-slate-500 dark:border-slate-800 dark:text-slate-400">
      <div className="mx-auto flex max-w-7xl flex-col gap-2 px-4 md:flex-row md:items-center md:justify-between">
        <div>AI World Cup is a manual, offline LLM prediction benchmark.</div>
        <a className="text-pitch hover:underline dark:text-emerald-300" href="#" aria-label="GitHub repository">
          GitHub repository
        </a>
      </div>
    </footer>
  );
}
