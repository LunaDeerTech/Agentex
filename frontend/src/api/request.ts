import axios, { type AxiosInstance, type AxiosRequestConfig, type AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import router from '@/router'

// Response interface following API design
export interface ApiResponse<T = unknown> {
  code: number
  message: string
  data: T
}

// Error codes mapping
const ERROR_MESSAGES: Record<number, string> = {
  40001: '无效的请求参数',
  40101: '未授权访问',
  40102: 'Token 已过期',
  40103: '无效的 Token',
  40301: '权限不足',
  40401: '资源不存在',
  50001: '服务器内部错误',
  50002: '数据库错误',
  50003: '外部服务错误',
}

// Create axios instance
const request: AxiosInstance = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
request.interceptors.request.use(
  (config) => {
    const userStore = useUserStore()
    const token = userStore.getToken()

    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    return config
  },
  (error: unknown) => {
    return Promise.reject(error)
  }
)

// Response interceptor
request.interceptors.response.use(
  (response: AxiosResponse<ApiResponse>) => {
    const { code, message, data } = response.data

    // Success
    if (code === 0) {
      return data as AxiosResponse
    }

    // Business error
    const errorMessage = ERROR_MESSAGES[code] || message || '请求失败'
    ElMessage.error(errorMessage)

    return Promise.reject(new Error(errorMessage))
  },
  (error: unknown) => {
    // Network error or server error
    const axiosError = error as { response?: { status: number; data?: { message?: string } }; request?: unknown }
    if (axiosError.response) {
      const { status, data } = axiosError.response

      switch (status) {
        case 401:
          // Unauthorized - redirect to login
          ElMessage.error('登录已过期，请重新登录')
          useUserStore().logout()
          router.push('/login')
          break
        case 403:
          ElMessage.error('权限不足')
          break
        case 404:
          ElMessage.error('请求的资源不存在')
          break
        case 500:
          ElMessage.error(data?.message || '服务器内部错误')
          break
        default:
          ElMessage.error(data?.message || '请求失败')
      }
    } else if (axiosError.request) {
      ElMessage.error('网络连接失败，请检查网络')
    } else {
      ElMessage.error('请求配置错误')
    }

    return Promise.reject(error)
  }
)

// HTTP methods wrapper
export const http = {
  get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    return request.get(url, config)
  },

  post<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> {
    return request.post(url, data, config)
  },

  put<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> {
    return request.put(url, data, config)
  },

  patch<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> {
    return request.patch(url, data, config)
  },

  delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    return request.delete(url, config)
  },
}

export default request
