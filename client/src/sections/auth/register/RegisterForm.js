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
import { register } from '../../../services/auth'

// Utils
import {
  validateName,
  validateUsername, 
  validatePassword
} from '../../../utils/validate'
import {
  setToken
} from '../../../utils/auth'

// ----------------------------------------------------------------------

export default function RegisterForm() {

  const navigate = useNavigate()

  // States
  const [showPassword, setShowPassword] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const [name, setName] = useState('')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [password2, setPassword2] = useState('')

  const [nameError, setNameError] = useState(false)
  const [usernameError, setUsernameError] = useState(false)
  const [passwordError, setPasswordError] = useState(false)
  const [password2Error, setPassword2Error] = useState(false)

  
  const [nameErrorMessage, setNameErrorMessage] = useState('')
  const [usernameErrorMessage, setUsernameErrorMessage] = useState('')
  const [passwordErrorMessage, setPasswordErrorMessage] = useState('')
  const [password2ErrorMessage, setPassword2ErrorMessage] = useState('')

  const [errorMessage, setErrorMessage] = useState('')

  // Handle functions
  const handleClick = async () => {
    setIsSubmitting(true)

    try{
      // Validate inputs
      if (!name || !username || !password || !password2) {
        if (!name) {
          setNameError(true)
          setNameErrorMessage('Name is empty!')
        }
        if (!username) {
          setUsernameError(true)
          setUsernameErrorMessage('Username is empty!')
        }
        if (!password) {
          setPasswordError(true)
          setPasswordErrorMessage('Password is empty!')
        }
        if (!password2) {
          setPassword2Error(true)
          setPassword2ErrorMessage('Please retype password!')
        }

        return null
      }

      const nameResult = validateName(name)
      const usernameResult = validateUsername(username)
      const passwordResult = validatePassword(password)
      const password2Result = validatePassword(password2)
      
      if (!nameResult.success ||
        !usernameResult.success || 
        !passwordResult.success || 
        !password2Result.success
      ) {

        if (!nameResult.success) {
          setNameError(true)
          setNameErrorMessage(nameResult.message)
        }

        if (!usernameResult.success) {
          setUsernameError(true)
          setUsernameErrorMessage(usernameResult.message)
        }

        if (!passwordResult.success) {
          setPasswordError(true)
          setPasswordErrorMessage(passwordResult.message)
        }

        if (!password2Result.success) {
          setPassword2Error(true)
          setPassword2ErrorMessage(password2Result.message)
        }

        return null
      }

      if (password !== password2) {
        setPassword2Error(true)
        setPassword2ErrorMessage("Retyped password unmatched!")
        return null
      }
      
      // Reset error
      setNameError(false)
      setUsernameError(false)
      setPasswordError(false)
      setPassword2Error(false)

      setNameErrorMessage('')
      setUsernameErrorMessage('')
      setPasswordErrorMessage('')
      setPassword2ErrorMessage('')

      // Call API
      const response = await register(name, username, password)

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
          name="name" 
          label="Name" 
          value={name} 
          onInput={(e) => setName(e.target.value)} 
          error={nameError}
          helperText={nameErrorMessage}
        />

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

        <TextField
          name="retype-password"
          label="Retype Password"
          value={password2}
          error={password2Error}
          helperText={password2ErrorMessage}
          onInput={(e) => setPassword2(e.target.value)}
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
        Sign up
      </LoadingButton>
    </>
  );
}
