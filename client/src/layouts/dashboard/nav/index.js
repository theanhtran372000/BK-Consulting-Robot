import PropTypes from 'prop-types';
import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';

// @mui
import { styled, alpha } from '@mui/material/styles';
import { 
  Box, 
  Link, 
  Drawer, 
  Typography, 
  Avatar,  
} from '@mui/material';

// hooks
import useResponsive from '../../../hooks/useResponsive';

// components
import Logo from '../../../components/logo';
import Scrollbar from '../../../components/scrollbar';
import NavSection from '../../../components/nav-section';
import SystemSelect from './SystemSelect'
import DateTimeSelect from './DateTimeSelect';

//
import navConfig from './config';

// ----------------------------------------------------------------------

const NAV_WIDTH = 280;

const StyledAccount = styled('div')(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  padding: theme.spacing(2, 2.5),
  borderRadius: Number(theme.shape.borderRadius) * 1.5,
  backgroundColor: alpha(theme.palette.grey[500], 0.12),
}));

// ----------------------------------------------------------------------

Nav.propTypes = {
  openNav: PropTypes.bool,
  onCloseNav: PropTypes.func,
  user: PropTypes.object,
  from: PropTypes.object,
  to: PropTypes.object,
  systemList: PropTypes.array,
  selectedIndex: PropTypes.number,
  handleChangeSystem: PropTypes.func,
  handleFromChange: PropTypes.func,
  handleToChange: PropTypes.func,
};

export default function Nav({ 
  systemList, selectedIndex, 
  handleChangeSystem, 
  handleFromChange, handleToChange,
  user, from, to,
  openNav, onCloseNav 
}) {
  const { pathname } = useLocation();

  const isDesktop = useResponsive('up', 'lg');

  useEffect(() => {
    if (openNav) {
      onCloseNav();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pathname]);

  const renderContent = (
    <Scrollbar
      sx={{
        height: 1,
        '& .simplebar-content': { height: 1, display: 'flex', flexDirection: 'column' },
      }}
    >
      {/* Logo */}
      <Box sx={{ px: 2.5, py: 3, display: 'inline-flex' }}>
        <Logo />
      </Box>

      {/* User info */}
      <Box sx={{ mb: 5, mx: 2.5 }}>
        <Link underline="none">
          <StyledAccount>
            <Avatar src='/assets/illustrations/illustration_avatar.png' alt="photoURL" />

            <Box sx={{ ml: 2 }}>
              <Typography variant="subtitle2" sx={{ color: 'text.primary' }}>
                {user? user.name : 'Loading...'}
              </Typography>

              <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                Admin
              </Typography>
            </Box>
          </StyledAccount>
        </Link>
      </Box>

      {/* System configs */}
      <Typography
       variant='h6'
       sx={{
        ml: 2,
        mb: 1
       }}
      >
        System configs
      </Typography>
      
      <SystemSelect systemList={systemList} selectedIndex={selectedIndex} handleChangeSystem={handleChangeSystem} />

      <DateTimeSelect title='From' bindTime={from} onChangeTime={handleFromChange} />
      <DateTimeSelect title='To' bindTime={to} onChangeTime={handleToChange} />

      {/* System logs */}
      <Typography
       variant='h6'
       sx={{
        ml: 2,
        mb: 1,
        mt: 4
       }}
      >
        System logs
      </Typography>

      <NavSection data={navConfig} />

    </Scrollbar>
  );

  return (
    <Box
      component="nav"
      sx={{
        flexShrink: { lg: 0 },
        width: { lg: NAV_WIDTH },
      }}
    >
      {isDesktop ? (
        <Drawer
          open
          variant="permanent"
          PaperProps={{
            sx: {
              width: NAV_WIDTH,
              bgcolor: 'background.default',
              borderRightStyle: 'dashed',
            },
          }}
        >
          {renderContent}
        </Drawer>
      ) : (
        <Drawer
          open={openNav}
          onClose={onCloseNav}
          ModalProps={{
            keepMounted: true,
          }}
          PaperProps={{
            sx: { width: NAV_WIDTH },
          }}
        >
          {renderContent}
        </Drawer>
      )}
    </Box>
  );
}
