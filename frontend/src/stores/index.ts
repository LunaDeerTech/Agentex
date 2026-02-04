import { createPinia } from 'pinia'

export const pinia = createPinia()

// Re-export stores
export * from './user'
