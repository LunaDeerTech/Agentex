<script setup lang="ts">
  import { onMounted } from 'vue'
  import { RouterView } from 'vue-router'
  import { useAppStore } from './stores'

  const appStore = useAppStore()

  onMounted(() => {
    // Initialize dark theme
    appStore.initTheme()
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
