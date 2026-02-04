import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'home',
    component: () => import('@/views/HomeView.vue'),
    meta: { title: 'Agentex' },
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/auth/LoginView.vue'),
    meta: { title: '登录 - Agentex', guest: true },
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('@/views/auth/RegisterView.vue'),
    meta: { title: '注册 - Agentex', guest: true },
  },
  {
    path: '/chat',
    name: 'chat',
    component: () => import('@/views/ChatView.vue'),
    meta: { title: '对话 - Agentex', requiresAuth: true },
  },
  {
    path: '/settings',
    name: 'settings',
    component: () => import('@/views/settings/SettingsLayout.vue'),
    meta: { title: '设置 - Agentex', requiresAuth: true },
    children: [
      {
        path: '',
        redirect: '/settings/profile',
      },
      {
        path: 'profile',
        name: 'settings-profile',
        component: () => import('@/views/settings/ProfileView.vue'),
        meta: { title: '个人信息 - Agentex' },
      },
      {
        path: 'models',
        name: 'settings-models',
        component: () => import('@/views/settings/ModelsView.vue'),
        meta: { title: '模型管理 - Agentex' },
      },
      {
        path: 'mcp',
        name: 'settings-mcp',
        component: () => import('@/views/settings/MCPView.vue'),
        meta: { title: 'MCP 连接 - Agentex' },
      },
      {
        path: 'knowledge',
        name: 'settings-knowledge',
        component: () => import('@/views/settings/KnowledgeView.vue'),
        meta: { title: '知识库 - Agentex' },
      },
      {
        path: 'skills',
        name: 'settings-skills',
        component: () => import('@/views/settings/SkillsView.vue'),
        meta: { title: 'SKILL 管理 - Agentex' },
      },
      {
        path: 'rules',
        name: 'settings-rules',
        component: () => import('@/views/settings/RulesView.vue'),
        meta: { title: '规则引擎 - Agentex' },
      },
    ],
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('@/views/NotFoundView.vue'),
    meta: { title: '页面不存在 - Agentex' },
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

// Navigation guards
router.beforeEach((to, _from, next) => {
  // Update document title
  document.title = (to.meta.title as string) || 'Agentex'
  next()
})

export default router
