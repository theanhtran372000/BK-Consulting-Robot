import { Outlet, RouterProvider } from 'react-router-dom';
import { HelmetProvider } from 'react-helmet-async';
import { LocalizationProvider } from '@mui/x-date-pickers';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs'

// routes
import Router from './routes';

// providers
import ThemeProvider from './theme';

// components
import { StyledChart } from './components/chart';
import ScrollToTop from './components/scroll-to-top';

// ----------------------------------------------------------------------

export function AppLayout() {
  return (
    <LocalizationProvider dateAdapter={AdapterDayjs}>
      <HelmetProvider>  
        <ThemeProvider>
            <ScrollToTop />
            <StyledChart />
            <Outlet />
        </ThemeProvider>
      </HelmetProvider>
    </LocalizationProvider>
  );
}

export default function App(){
  return <RouterProvider router={Router()} />
}