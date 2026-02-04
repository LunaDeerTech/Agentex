import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export type Theme = 'dark' | 'light'

export interface AppState {
  sidebarCollapsed: boolean
  theme: Theme
  loading: boolean
  loadingText: string
}

export const useAppStore = defineStore('app', () => {
  // State
  const sidebarCollapsed = ref(false)
  const theme = ref<Theme>('dark')
  const globalLoading = ref(false)
  const loadingText = ref('')

  // Getters
  const isDarkTheme = computed(() => theme.value === 'dark')

  // Actions
  function toggleSidebar() {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }

  function setSidebarCollapsed(collapsed: boolean) {
    sidebarCollapsed.value = collapsed
  }

  function setTheme(newTheme: Theme) {
    theme.value = newTheme
    document.documentElement.classList.toggle('dark', newTheme === 'dark')
  }

  function setLoading(loading: boolean, text = '') {
    globalLoading.value = loading
    loadingText.value = text
  }

  // 初始化主题
  function initTheme() {
    // 默认深色主题
    document.documentElement.classList.add('dark')
  }

  return {
    // State
    sidebarCollapsed,
    theme,
    globalLoading,
    loadingText,
    // Getters
    isDarkTheme,
    // Actions
    toggleSidebar,
    setSidebarCollapsed,
    setTheme,
    setLoading,
    initTheme
  }
})
