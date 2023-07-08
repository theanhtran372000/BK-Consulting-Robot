import configs from '../configs'

// Utils
import { getToken } from '../utils/auth'

export const login = async (username, password) => {
    
    // Prepare data
    const formData = new FormData()
    formData.append('username', username)
    formData.append('password', password)

    // Call API
    const response = await fetch(`http://${configs.server.host}:${configs.server.port}/user/auth/login`, 
      {
        method: 'POST',
        body: formData,
      }
    );

    return response
}

export const register = async (name, username, password) => {
    
  // Prepare data
  const formData = new FormData()
  formData.append('name', name)
  formData.append('username', username)
  formData.append('password', password)

  // Call API
  const response = await fetch(
    `http://${configs.server.host}:${configs.server.port}/user/auth/register`, 
    {
      method: 'POST',
      body: formData,
    }
  );

  return response
}

export const checkAuth = async () => {
  const token = getToken()

  if (!token) {
    return {
      success: false,
      message: 'Access token not found!'
    }
  }
  console.log(`Found token on local: ${token}`)

  const response = await fetch(
    `http://${configs.server.host}:${configs.server.port}/user/info/get`,
    {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`
      },
    }
  )

  const content = await (response.json())
  if (!content.success) {
    console.log('User unauthenticated!')
  }
  else{
    console.log('Fail to authenticate!')
  }

  return content
}