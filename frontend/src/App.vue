<script setup lang="ts">
  import { onMounted } from 'vue'
  import { RouterView } from 'vue-router'
  import { useAppStore } from '@/stores/modules/app'
  import { useAuthStore } from '@/stores/auth'

  const appStore = useAppStore()
  const authStore = useAuthStore()

  onMounted(() => {
    // Initialize dark theme
    appStore.initTheme()

    // Fetch user info if authenticated
    if (authStore.isAuthenticated) {
      authStore.fetchUser()
    }
  })
</script>

<template>
  <RouterView />
</template>

<style>
  #app {
    min-height: 100vh;
  }
</style>
