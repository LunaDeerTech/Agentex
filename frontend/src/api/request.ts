import axios, { type InternalAxiosRequestConfig, type AxiosResponse } from 'axios'
import { useAuthStore } from '@/stores/auth'

// Define standard response structure
export interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
}

const request = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api/v1',
  timeout: 20000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request Interceptor
request.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const authStore = useAuthStore()
    const token = authStore.token

    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

// Response Interceptor
request.interceptors.response.use(
  (response: AxiosResponse) => {
    const res = response.data as ApiResponse
    
    // Backend convention: code 0 is success
    if (res.code === 0) {
      return res.data
    }
    
    // If it's not code 0, it's an error
    if (res.code !== undefined && res.code !== 0) {
       console.error(`API Error [${res.code}]: ${res.message}`)
       return Promise.reject(new Error(res.message || 'Error'))
    }

    // Fallback for responses that don't follow the wrapper structure
    return response.data
  },
  (error) => {
    const authStore = useAuthStore()
    console.error('Response error:', error)
    
    if (error.response?.status === 401) {
      authStore.logout()
      if (!window.location.pathname.includes('/login')) {
         window.location.href = '/login'
      }
    }
    
    const message = error.response?.data?.message || error.message || 'Network Error'
    return Promise.reject(new Error(message))
  }
)

export default request
