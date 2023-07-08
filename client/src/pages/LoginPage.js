import { useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';

// @mui
import { styled } from '@mui/material/styles';
import { Container, Typography } from '@mui/material';

// hooks
import useResponsive from '../hooks/useResponsive';

// components
import Logo from '../components/logo';

// sections
import { LoginForm } from '../sections/auth/login';

// Services
import { checkAuth } from '../services/auth';

// Utils
import { deleteToken } from '../utils/auth';

// ----------------------------------------------------------------------

const StyledRoot = styled('div')(({ theme }) => ({
  [theme.breakpoints.up('md')]: {
    display: 'flex',
  },
}));

const StyledSection = styled('div')(({ theme }) => ({
  width: '100%',
  maxWidth: 480,
  display: 'flex',
  flexDirection: 'column',
  justifyContent: 'center',
  boxShadow: theme.customShadows.card,
  backgroundColor: theme.palette.background.default,
}));

const StyledContent = styled('div')(({ theme }) => ({
  maxWidth: 480,
  margin: 'auto',
  minHeight: '100vh',
  display: 'flex',
  justifyContent: 'center',
  flexDirection: 'column',
  padding: theme.spacing(12, 0),
}));

// ----------------------------------------------------------------------

export default function LoginPage() {

  const navigate = useNavigate()
  const mdUp = useResponsive('up', 'md');

  useEffect(() => {
    const getAuth = async () => {
      const result = await checkAuth()

      if (!result.success) {
        console.log(`Authentication failed: ${ result.message }`)
        deleteToken()
        return null
      }

      console.log('User authenticated!')
      return navigate('/dashboard')
    }

    getAuth()
  }, [navigate])

  return (
    <>
      <Helmet>
        <title> Sign in </title>
      </Helmet>

      <StyledRoot>
        <Logo
          sx={{
            position: 'fixed',
            top: { xs: 16, sm: 24, md: 40 },
            left: { xs: 16, sm: 24, md: 40 },
          }}
        />

        {mdUp && (
          <StyledSection>
            <Typography variant="h3" sx={{ px: 5, mt: 10, mb: 5 }}>
              Hi, Welcome Back
            </Typography>
            <img src="/assets/illustrations/illustration_login.svg" alt="login" />
          </StyledSection>
        )}

        <Container maxWidth="sm">
          <StyledContent>
            <Typography  
              sx={{
                fontWeight: 600
              }} 
              variant="h4" 
              gutterBottom
            >
              Sign in as Admin
            </Typography>

            <Typography variant="body2" sx={{ mb: 5 }}>
              Don’t have an account? {''}
              <Link to='/register'>Sign up here</Link>
            </Typography>

            <LoginForm />

          </StyledContent>
        </Container>
      </StyledRoot>
    </>
  );
}
