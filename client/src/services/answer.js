import configs from '../configs'

export const extractKeywords = async (data) => {

  // Call API
  const response = await fetch(
    `http://${configs.server.host}:${configs.server.port}/answer/standard/extract`, 
    {
      method: 'POST',
      body: JSON.stringify({ data }),
      headers: {
        "Content-Type": "application/json"
      }
    }
  );

  return response
}