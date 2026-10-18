import api from './api'

export const registerUser = async (userData) => {
  const response = await api.post('/accounts/register/', userData)
  return response.data
}

export const loginUser = async (credentials) => {
  const response = await api.post('/accounts/login/', credentials)

  const { access, refresh } = response.data

  localStorage.setItem('access_token', access)
  localStorage.setItem('refresh_token', refresh)

  return response.data
}

export const getProfile = async () => {
  const response = await api.get('/accounts/profile/')
  return response.data
}

export const refreshAccessToken = async () => {
  const refreshToken = localStorage.getItem('refresh_token')

  const response = await api.post('/accounts/token/refresh/', {
    refresh: refreshToken,
  })

  localStorage.setItem('access_token', response.data.access)

  return response.data
}

export const logoutUser = async () => {
  const refreshToken = localStorage.getItem('refresh_token')

  try {
    await api.post('/accounts/logout/', {
      refresh: refreshToken,
    })
  } finally {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }
}