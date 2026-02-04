import { createPinia } from 'pinia'

const pinia = createPinia()

export default pinia

// 导出所有 stores
export * from './modules/user'
export * from './modules/session'
export * from './modules/app'
