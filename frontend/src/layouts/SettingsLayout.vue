<script setup lang="ts">
  import { ArrowLeft } from 'lucide-vue-next'
  import SettingsMenu from '@/components/layout/SettingsMenu.vue'
</script>

<template>
  <div class="flex h-screen w-full bg-background text-foreground font-sans overflow-hidden">
    <!-- Sidebar / Menu -->
    <div class="flex flex-col w-64 border-r border-border bg-card shrink-0">
      <div class="p-6 pb-2">
        <router-link
          to="/"
          class="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors mb-6 group w-fit"
        >
          <ArrowLeft class="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
          Back to Chat
        </router-link>
        <h2 class="text-xl font-semibold tracking-tight px-1">Settings</h2>
      </div>
      <SettingsMenu />
    </div>

    <!-- Content -->
    <div class="flex-1 overflow-y-auto min-w-0 bg-background">
      <div class="max-w-4xl mx-auto px-8 py-10">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </div>
    </div>
  </div>
</template>

<style scoped>
  .fade-enter-active,
  .fade-leave-active {
    transition: opacity 0.15s ease;
  }

  .fade-enter-from,
  .fade-leave-to {
    opacity: 0;
  }
</style>
