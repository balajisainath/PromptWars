import axios from 'axios'
import { auth } from './firebase'
import { isDevMode } from './auth'

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
})

api.interceptors.request.use(async (config) => {
  // In dev mode, read token from localStorage (set by auth store)
  if (isDevMode()) {
    const stored = typeof window !== 'undefined' ? localStorage.getItem('travelai-token') : null
    if (stored) {
      config.headers.Authorization = `Bearer ${stored}`
    }
    return config
  }

  const user = auth.currentUser
  if (user) {
    const token = await user.getIdToken()
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401 && !isDevMode()) {
      auth.signOut()
    }
    return Promise.reject(error)
  }
)

export default api
