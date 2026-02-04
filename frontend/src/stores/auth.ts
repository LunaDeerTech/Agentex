import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import {
  login as loginApi,
  register as registerApi,
  getUserInfo,
  type LoginParams,
  type RegisterParams,
  type User
} from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('token'))
  const isLoading = ref(false)

  // Getters
  const isAuthenticated = computed(() => !!token.value)

  // Actions
  async function login(params: LoginParams) {
    isLoading.value = true
    try {
      const res = await loginApi(params)
      // Assuming res is the data returned by axios interceptor (TokenResponse)
      // Wait, api/auth.ts types suggest it returns ApiResponse<TokenResponse> or just TokenResponse?
      // In request.ts I returned response.data.
      // So if backend returns { access_token: ... }, res is that object.
      // NOTE: Backend typically returns the model directly or wrapped.
      // Based on FastAPI `response_model=TokenResponse`, it returns JSON implementation of TokenResponse directly.

      const accessToken = res.access_token
      setToken(accessToken)

      // Fetch user info immediately after login
      await fetchUser()
      return true
    } catch (error) {
      throw error
    } finally {
      isLoading.value = false
    }
  }

  async function register(params: RegisterParams) {
    isLoading.value = true
    try {
      const res = await registerApi(params)
      // Registration might return user+token or just user.
      // Backend `auth.py` says `return result` which is `RegisterResponse`.
      // `RegisterResponse` contains `user` and `tokens` usually?
      // Let's assume it logs in automatically or we need to login.
      // Checking schemas/auth.py or api/v1/auth.py in my thought process earlier...
      // The register endpoint returns `RegisterResponse`.
      // Usually that means we can set token.

      // If endpoint returns tokens:
      if (res && (res as any).tokens) {
        setToken((res as any).tokens.access_token)
        user.value = (res as any).user
      }
      return true
    } catch (error) {
      throw error
    } finally {
      isLoading.value = false
    }
  }

  async function fetchUser() {
    try {
      const userData = await getUserInfo()
      // userData is User object
      user.value = userData
    } catch (error) {
      // If 401, logout
      logout()
    }
  }

  function setToken(newToken: string) {
    token.value = newToken
    localStorage.setItem('token', newToken)
  }

  function logout() {
    user.value = null
    token.value = null
    localStorage.removeItem('token')
  }

  return {
    user,
    token,
    isLoading,
    isAuthenticated,
    login,
    register,
    logout,
    fetchUser
  }
})
