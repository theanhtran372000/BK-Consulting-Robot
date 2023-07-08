import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

// @mui
import { 
  Stack, 
  IconButton, 
  InputAdornment, 
  TextField,
  Typography
} from '@mui/material';
import { LoadingButton } from '@mui/lab';

// components
import Iconify from '../../../components/iconify';

// Services
import { login } from '../../../services/auth'

// Utils
import {
  validateUsername, 
  validatePassword
} from '../../../utils/validate'
import {
  setToken
} from '../../../utils/auth'


// ----------------------------------------------------------------------

export default function LoginForm() {

  const navigate = useNavigate()

  // States
  const [showPassword, setShowPassword] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')

  const [usernameError, setUsernameError] = useState(false)
  const [passwordError, setPasswordError] = useState(false)

  const [usernameErrorMessage, setUsernameErrorMessage] = useState('')
  const [passwordErrorMessage, setPasswordErrorMessage] = useState('')

  const [errorMessage, setErrorMessage] = useState('')

  // Handle functions
  const handleClick = async () => {
    setIsSubmitting(true)

    try{
      // Validate inputs
      if (!username || !password) {
        if (!username) {
          setUsernameError(true)
          setUsernameErrorMessage('Username is empty!')
        }
        if (!password) {
          setPassword(true)
          setPasswordErrorMessage('Password is empty!')
        }

        return null
      }

      const usernameResult = validateUsername(username)
      const passwordResult = validatePassword(password)
      
      if (!usernameResult.success || !passwordResult.success) {
        if (!usernameResult.success) {
          setUsernameError(true)
          setUsernameErrorMessage(usernameResult.message)
        }

        if (!passwordResult.success) {
          setPasswordError(true)
          setPasswordErrorMessage(passwordResult.message)
        }

        return null
      }

      // Reset error
      setUsernameError(false)
      setPasswordError(false)
      setUsernameErrorMessage('')
      setPasswordErrorMessage('')

      // Call API
      const response = await login(username, password)

      const content = await (response.json())
      
      if (!content.success) {
        setErrorMessage(content.message)
        return null
      } 
      setErrorMessage('')

      const { access_token: token } = content.data
      setToken(token)
      return navigate('/dashboard')
    }
    
    finally{
      setIsSubmitting(false)
    }
  };

  return (
    <>
      <Stack spacing={3}>
        <TextField 
          name="username" 
          label="Username" 
          value={username} 
          onInput={(e) => setUsername(e.target.value)} 
          error={usernameError}
          helperText={usernameErrorMessage}
        />

        <TextField
          name="password"
          label="Password"
          value={password}
          error={passwordError}
          helperText={passwordErrorMessage}
          onInput={(e) => setPassword(e.target.value)}
          type={showPassword ? 'text' : 'password'}
          InputProps={{
            endAdornment: (
              <InputAdornment position="end">
                <IconButton onClick={() => setShowPassword(!showPassword)} edge="end">
                  <Iconify icon={showPassword ? 'eva:eye-fill' : 'eva:eye-off-fill'} />
                </IconButton>
              </InputAdornment>
            ),
          }}
        />

      </Stack>

      {errorMessage && 
        <Typography variant='body2' sx={{
          mt: 3,
          ml: 0.5,
          color: 'red'
        }}>
          {errorMessage}
        </Typography>
      }

      <LoadingButton 
        fullWidth size="large" 
        type="submit" 
        variant="contained" 
        onClick={handleClick}
        loading={isSubmitting}
        sx={{
          mt: errorMessage? 1 : 4
        }}
      >
        Sign in
      </LoadingButton>
    </>
  );
}
