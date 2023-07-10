import { Navigate, createBrowserRouter } from 'react-router-dom';
// layouts
import DashboardLayout from './layouts/dashboard';
import SimpleLayout from './layouts/simple';
import { AppLayout } from './App';

// Pages
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage'

import Page404 from './pages/Page404';
import ErrorPage from './pages/ErrorPage';

import FaceTrackPage from './pages/FaceTrackPage'
import StatsPage from './pages/StatsPage';
import HistoryPage from './pages/HistoryPage';

// ----------------------------------------------------------------------

export default function Router() {
  const routes = createBrowserRouter([
    {
      path: '/',
      element: <AppLayout />,
      // errorElement: <Navigate to='/500' />,
      children: [
        {
          path: 'dashboard',
          element: <DashboardLayout />,
          children: [
            { 
              element: <Navigate to="/dashboard/history" />, 
              index: true 
            },
            { 
              path: 'track', 
              element: <FaceTrackPage /> 
            },
            { 
              path: 'stats', 
              element: <StatsPage /> 
            },
            { 
              path: 'history', 
              element: <HistoryPage /> 
            },
          ],
        },
        {
          element: <SimpleLayout />,
          children: [
            { 
              element: <Navigate to="/login" />, 
              index: true 
            },
            {
              path: 'login',
              // loader: checkAuthLoader,
              element: <LoginPage />,
            },
            {
              path: 'register',
              // loader: checkAuthLoader,
              element: <RegisterPage />
            },
            { 
              path: '404', 
              element: <Page404 /> 
            },
            {
              path: '500',
              element: <ErrorPage />
            },
            { 
              path: '*', 
              element: <Navigate to="/404" /> 
            },
          ],
        },
        
      ]
    }
  ]);

  return routes;
}
