import request from './request'
import type { ApiResponse } from './request'

// Model Interfaces (aligned with backend schemas)

export interface User {
  id: string
  username: string
  email: string
  is_active: boolean
  is_superuser: boolean
  created_at: string
  last_login_at?: string
}

export interface LoginParams {
  username: string // Supports email or username in many systems, but schema said username
  password: string
}

export interface RegisterParams {
  username: string
  email: string
  password: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

// Responses
export type LoginResponse = ApiResponse<TokenResponse>
export type RegisterResponse = ApiResponse<{
  user: User
  tokens: TokenResponse
}>
export type UserInfoResponse = ApiResponse<User>

// API Functions

export const login = (data: LoginParams) => {
  return request.post<TokenResponse>('/auth/login', data)
}

export const register = (data: RegisterParams) => {
  return request.post<RegisterResponse>('/auth/register', data) // Note: response structure might be wrapped or direct, request.ts handles ApiResponse unpacking usually or we handle it.
  // Checking request.ts: it uses response.data usually or interceptors return response.
}

export const getUserInfo = () => {
  return request.get<User>('/users/me')
}

export const logout = () => {
  // If there is a backend logout, call it here.
  // Otherwise just clear client side.
  // Sometimes: return request.post('/auth/logout')
  // Design docs didn't mention logout endpoint, so client-side only for now.
  return Promise.resolve()
}
