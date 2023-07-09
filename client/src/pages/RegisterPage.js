import { useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';

// @mui
import { styled } from '@mui/material/styles';
import { Container, Typography } from '@mui/material';

// hooks
import useResponsive from '../hooks/useResponsive';

// sections
import { RegisterForm } from '../sections/auth/register';

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
        <title> Sign up </title>
      </Helmet>

      <StyledRoot>

        {mdUp && (
          <StyledSection>
            <Typography variant="h3" sx={{ px: 5, mt: 10, mb: 5 }}>
              Step in line...
            </Typography>
            <img src="/assets/illustrations/illustration_register.svg" alt="register" />
          </StyledSection>
        )}

        <Container maxWidth="sm">
          <StyledContent>
            <Typography  
              sx={{
                fontWeight: 600,
                mb: 2
              }} 
              variant="h4" 
              gutterBottom
            >
              Sign up as Admin
            </Typography>

            <Typography variant="body2" sx={{ mb: 5 }}>
              Already have account? {''}
              <Link to='/login'>Sign in here</Link>
            </Typography>

            <RegisterForm />
          </StyledContent>
        </Container>
      </StyledRoot>
    </>
  );
}
