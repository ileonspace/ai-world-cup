import type { RouteObject } from 'react-router-dom';
import { Layout } from './components/Layout';
import { About } from './routes/About';
import { DataSnapshot } from './routes/DataSnapshot';
import { Home } from './routes/Home';
import { Leaderboard } from './routes/Leaderboard';
import { MatchDetails } from './routes/MatchDetails';
import { Methodology } from './routes/Methodology';
import { Predictions } from './routes/Predictions';
import { TournamentExplorer } from './routes/TournamentExplorer';

export const App: RouteObject[] = [
  {
    path: '/',
    element: <Layout />,
    children: [
      { index: true, element: <Home /> },
      { path: 'leaderboard', element: <Leaderboard /> },
      { path: 'tournament', element: <TournamentExplorer /> },
      { path: 'predictions', element: <Predictions /> },
      { path: 'matches/:matchNumber', element: <MatchDetails /> },
      { path: 'methodology', element: <Methodology /> },
      { path: 'prompt-protocol', element: <Methodology /> },
      { path: 'data-snapshot', element: <DataSnapshot /> },
      { path: 'about', element: <About /> }
    ]
  }
];
