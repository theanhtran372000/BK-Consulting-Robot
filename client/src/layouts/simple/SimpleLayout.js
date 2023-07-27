import { Outlet } from 'react-router-dom';

// @mui
import { styled, useTheme } from '@mui/material/styles';
import { 
  Box, 
  Typography, 
  Avatar,  
} from '@mui/material';

// ----------------------------------------------------------------------

const StyledHeader = styled('header')(({ theme }) => ({
  top: 0,
  left: 0,
  lineHeight: 0,
  width: '100%',
  position: 'absolute',
  padding: theme.spacing(3, 3, 0),
  [theme.breakpoints.up('sm')]: {
    padding: theme.spacing(5, 5, 0),
  },
}));

// ----------------------------------------------------------------------

export default function SimpleLayout() {

  const theme = useTheme()

  return (
    <>
      <StyledHeader>
        <Box sx={{ 
          display: 'inline-flex', alignItems: 'center', justifyContent: 'left' 
        }}>
          <Avatar sx={{
            width: theme.spacing(8),
            height: theme.spacing(8)
          }} src='/favicon/favicon.png' alt="photoURL" />

          <Typography 
            sx={{
              ml: 2
            }} variant='h4'
            color={theme.palette.info.main}
          >BK-Bot</Typography>
        </Box>
      </StyledHeader>

      <Outlet />
    </>
  );
}
