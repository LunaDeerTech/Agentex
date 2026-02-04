import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Chat',
    component: () => import('@/views/ChatView.vue'),
    meta: { requiresAuth: true, title: 'Chat - Agentex' }
  },
  {
    path: '/settings',
    component: () => import('@/layouts/SettingsLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        redirect: { name: 'SettingsProfile' }
      },
      {
        path: 'profile',
        name: 'SettingsProfile',
        component: () => import('@/views/settings/ProfileView.vue'),
        meta: { title: 'Settings - Profile' }
      },
      {
        path: 'api-keys',
        name: 'SettingsApiKeys',
        component: () => import('@/views/settings/ApiKeysView.vue'),
        meta: { title: 'Settings - API Keys' }
      },
      {
        path: ':category',
        name: 'SettingsCategory',
        component: () => import('@/views/settings/ApiKeysView.vue'), // Temporary placeholder
        meta: { title: 'Settings' }
      }
    ]
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/LoginView.vue'),
    meta: {
      title: 'Sign In - Agentex',
      guestOnly: true
    }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/auth/RegisterView.vue'),
    meta: {
      title: 'Sign Up - Agentex',
      guestOnly: true
    }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFoundView.vue'),
    meta: {
      title: '404 - Not Found'
    }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(_to, _from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// Navigation Guard
router.beforeEach((to, _from, next) => {
  // Update document title
  const title = to.meta.title as string | undefined
  if (title) {
    document.title = title
  }

  // Auth Guard
  const authStore = useAuthStore()

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else if (to.meta.guestOnly && authStore.isAuthenticated) {
    next('/')
  } else {
    next()
  }
})

export default router
