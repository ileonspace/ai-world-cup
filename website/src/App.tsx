import type { RouteObject } from 'react-router-dom';
import { Layout } from './components/Layout';
import { About } from './routes/About';
import { DataSnapshot } from './routes/DataSnapshot';
import { Fixtures } from './routes/Fixtures';
import { Groups } from './routes/Groups';
import { Home } from './routes/Home';
import { Knockout } from './routes/Knockout';
import { Leaderboard } from './routes/Leaderboard';
import { MatchDetails } from './routes/MatchDetails';
import { ModelComparison } from './routes/ModelComparison';
import { Predictions } from './routes/Predictions';
import { PromptProtocol } from './routes/PromptProtocol';

export const App: RouteObject[] = [
  {
    path: '/',
    element: <Layout />,
    children: [
      { index: true, element: <Home /> },
      { path: 'leaderboard', element: <Leaderboard /> },
      { path: 'models', element: <ModelComparison /> },
      { path: 'fixtures', element: <Fixtures /> },
      { path: 'predictions', element: <Predictions /> },
      { path: 'matches/:matchNumber', element: <MatchDetails /> },
      { path: 'groups', element: <Groups /> },
      { path: 'knockout', element: <Knockout /> },
      { path: 'prompt-protocol', element: <PromptProtocol /> },
      { path: 'data-snapshot', element: <DataSnapshot /> },
      { path: 'about', element: <About /> }
    ]
  }
];
