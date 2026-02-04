import axios, {
  type AxiosInstance,
  type AxiosRequestConfig,
  type AxiosResponse,
  type InternalAxiosRequestConfig
} from 'axios'
import { useUserStore } from '@/stores'

// API 响应标准格式
export interface ApiResponse<T = unknown> {
  code: number
  message: string
  data: T
}

// 分页响应格式
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  pageSize: number
  totalPages: number
}

// 错误码定义
export const ErrorCodes = {
  SUCCESS: 0,
  // 客户端错误 40xxx
  BAD_REQUEST: 40000,
  UNAUTHORIZED: 40100,
  FORBIDDEN: 40300,
  NOT_FOUND: 40400,
  VALIDATION_ERROR: 40001,
  // 服务端错误 50xxx
  INTERNAL_ERROR: 50000,
  SERVICE_UNAVAILABLE: 50300
} as const

// 创建 axios 实例
const request: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
request.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const userStore = useUserStore()
    const token = userStore.token

    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }

    return config
  },
  error => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response: AxiosResponse<ApiResponse>) => {
    const { code, message, data } = response.data

    // 业务成功
    if (code === ErrorCodes.SUCCESS) {
      return data as AxiosResponse
    }

    // 业务错误
    console.error(`API Error [${code}]: ${message}`)

    // 处理特定错误码
    if (code === ErrorCodes.UNAUTHORIZED) {
      const userStore = useUserStore()
      userStore.logout()
      window.location.href = '/login'
    }

    return Promise.reject(new Error(message))
  },
  error => {
    // 网络错误或服务器错误
    const message = error.response?.data?.message || error.message || 'Network error'
    console.error('Response error:', message)

    // 处理 401 未授权
    if (error.response?.status === 401) {
      const userStore = useUserStore()
      userStore.logout()
      window.location.href = '/login'
    }

    return Promise.reject(error)
  }
)

// 封装通用请求方法
export async function get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
  const response = await request.get<T, T>(url, config)
  return response
}

export async function post<T>(
  url: string,
  data?: unknown,
  config?: AxiosRequestConfig
): Promise<T> {
  const response = await request.post<T, T>(url, data, config)
  return response
}

export async function put<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> {
  const response = await request.put<T, T>(url, data, config)
  return response
}

export async function patch<T>(
  url: string,
  data?: unknown,
  config?: AxiosRequestConfig
): Promise<T> {
  const response = await request.patch<T, T>(url, data, config)
  return response
}

export async function del<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
  const response = await request.delete<T, T>(url, config)
  return response
}

// SSE 事件流处理（用于 AG-UI 协议）
export function createEventSource(
  url: string,
  onMessage: (event: MessageEvent) => void,
  onError?: (error: Event) => void
): EventSource {
  const userStore = useUserStore()
  const token = userStore.token
  const fullUrl = token ? `${url}${url.includes('?') ? '&' : '?'}token=${token}` : url

  const eventSource = new EventSource(fullUrl)

  eventSource.onmessage = onMessage
  eventSource.onerror = onError || (error => console.error('SSE error:', error))

  return eventSource
}

export default request
