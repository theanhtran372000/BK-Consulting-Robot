import configs from '../configs'

// Utils
import { getToken } from '../utils/auth'

export const listFaceTrackLog = async (systemId, from, to) => {
  // Get token
  const token = getToken()

  // Prepare data
  const formData = new FormData()
  formData.append('system_id', systemId)
  formData.append('from', from)
  formData.append('to', to)

  // Call API
  const response = await fetch(
    `http://${configs.server.host}:${configs.server.port}/system/log/list_face_track`, 
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      },
      body: formData
    }
  );

  return response
}

export const listStatsLog = async (systemId, from, to) => {
  // Get token
  const token = getToken()

  // Prepare data
  const formData = new FormData()
  formData.append('system_id', systemId)
  formData.append('from', from)
  formData.append('to', to)

  // Call API
  const response = await fetch(
    `http://${configs.server.host}:${configs.server.port}/system/log/list_stats`, 
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      },
      body: formData
    }
  );

  return response
}

export const listHistoryLog = async (systemId, from, to) => {
  // Get token
  const token = getToken()

  // Prepare data
  const formData = new FormData()
  formData.append('system_id', systemId)
  formData.append('from', from)
  formData.append('to', to)

  // Call API
  const response = await fetch(
    `http://${configs.server.host}:${configs.server.port}/system/log/list_history`, 
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      },
      body: formData
    }
  );

  return response
}