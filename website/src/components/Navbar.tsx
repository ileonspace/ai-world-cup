import { NavLink } from 'react-router-dom';
import { useState } from 'react';

const links = [
  ['/', 'Home'],
  ['/leaderboard', 'Leaderboard'],
  ['/tournament', 'Tournament'],
  ['/predictions', 'Predictions'],
  ['/methodology', 'Methodology'],
  ['/data-snapshot', 'Data'],
  ['/about', 'About']
];

export function Navbar() {
  const [open, setOpen] = useState(false);
  const navLinkClass = ({ isActive }: { isActive: boolean }) =>
    `rounded-md px-3 py-2 ${
      isActive
        ? 'bg-pitch text-white dark:bg-emerald-500 dark:text-slate-950'
        : 'text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-900'
    }`;

  return (
    <header className="border-b border-slate-200 bg-white/90 backdrop-blur dark:border-slate-800 dark:bg-slate-950/90">
      <div className="mx-auto max-w-7xl px-4 py-4">
        <div className="flex items-center justify-between gap-3">
          <NavLink to="/" className="text-xl font-bold tracking-tight text-pitch dark:text-emerald-300">
            AI World Cup
          </NavLink>
          <button
            type="button"
            aria-expanded={open}
            aria-label="Toggle navigation menu"
            className="rounded-md border border-slate-300 px-3 py-2 text-slate-700 md:hidden dark:border-slate-700 dark:text-slate-200"
            onClick={() => setOpen((value) => !value)}
          >
            <span className="block h-0.5 w-5 bg-current" />
            <span className="mt-1 block h-0.5 w-5 bg-current" />
            <span className="mt-1 block h-0.5 w-5 bg-current" />
          </button>
        </div>
        <nav className="mt-3 hidden flex-wrap gap-2 text-sm md:flex">
          {links.map(([to, label]) => (
            <NavLink
              key={to}
              to={to}
              className={navLinkClass}
            >
              {label}
            </NavLink>
          ))}
        </nav>
        {open ? (
          <nav className="mt-4 grid gap-2 rounded-lg border border-slate-200 bg-white p-3 text-sm shadow-sm md:hidden dark:border-slate-800 dark:bg-slate-950">
            {links.map(([to, label]) => (
              <NavLink
                key={to}
                to={to}
                className={navLinkClass}
                onClick={() => setOpen(false)}
              >
                {label}
              </NavLink>
            ))}
          </nav>
        ) : null}
      </div>
    </header>
  );
}
