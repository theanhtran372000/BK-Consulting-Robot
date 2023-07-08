import configs from '../configs'

// Utils
import { getToken } from '../utils/auth'

export const addSystem = async (systemId) => {
    
  // Get token
  const token = getToken()

  // Prepare data
  const formData = new FormData()
  formData.append('system_id', systemId)

  // Call API
  const response = await fetch(
    `http://${configs.server.host}:${configs.server.port}/system/info/add`, 
    {
      method: 'POST',
      body: formData,
      headers: {
        'Authorization': `Bearer ${token}`
      }
    }
  );

  return response
}

export const listSystem = async () => {
    
  // Get token
  const token = getToken()

  // Call API
  const response = await fetch(
    `http://${configs.server.host}:${configs.server.port}/system/info/list`, 
    {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    }
  );

  return response
}