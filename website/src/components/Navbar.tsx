import { NavLink } from 'react-router-dom';

const links = [
  ['/', 'Home'],
  ['/leaderboard', 'Leaderboard'],
  ['/tournament', 'Tournament'],
  ['/models', 'Models'],
  ['/fixtures', 'Fixtures'],
  ['/predictions', 'Predictions'],
  ['/groups', 'Groups'],
  ['/knockout', 'Knockout'],
  ['/methodology', 'Methodology'],
  ['/data-snapshot', 'Data'],
  ['/about', 'About']
];

export function Navbar() {
  return (
    <header className="border-b border-slate-200 bg-white/90 backdrop-blur dark:border-slate-800 dark:bg-slate-950/90">
      <div className="mx-auto flex max-w-7xl flex-col gap-3 px-4 py-4 md:flex-row md:items-center md:justify-between">
        <NavLink to="/" className="text-xl font-bold tracking-tight text-pitch dark:text-emerald-300">
          AI World Cup
        </NavLink>
        <nav className="flex flex-wrap gap-2 text-sm">
          {links.map(([to, label]) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `rounded-md px-3 py-2 ${
                  isActive
                    ? 'bg-pitch text-white dark:bg-emerald-500 dark:text-slate-950'
                    : 'text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-900'
                }`
              }
            >
              {label}
            </NavLink>
          ))}
        </nav>
      </div>
    </header>
  );
}
