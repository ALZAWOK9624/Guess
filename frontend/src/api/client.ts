/** Axios instance with auth interceptor. */

import axios from 'axios'
import type { AxiosInstance, InternalAxiosRequestConfig } from 'axios'

const apiClient: AxiosInstance = axios.create({
  baseURL: '/api/v1',
  headers: { 'Content-Type': 'application/json' },
})

// Request interceptor: attach auth token
apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const stored = localStorage.getItem('auth')
  if (stored) {
    try {
      const auth = JSON.parse(stored)
      if (auth.accessToken) {
        config.headers.Authorization = `Bearer ${auth.accessToken}`
      }
    } catch {
      // ignore parse errors
    }
  }
  return config
})

// Response interceptor: handle 401 with token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      const stored = localStorage.getItem('auth')
      if (stored) {
        try {
          const auth = JSON.parse(stored)
          if (auth.refreshToken) {
            const res = await axios.post('/api/v1/auth/refresh', {
              refresh_token: auth.refreshToken,
            })
            const newToken = res.data.access_token
            // Update localStorage
            auth.accessToken = newToken
            localStorage.setItem('auth', JSON.stringify(auth))
            originalRequest.headers.Authorization = `Bearer ${newToken}`
            return apiClient(originalRequest)
          }
        } catch {
          localStorage.removeItem('auth')
          // redirect to login handled by router guard in Story 1.5b
        }
      }
    }
    return Promise.reject(error)
  },
)

export default apiClient
