<script setup lang="ts">
  /**
   * ChatView - Main chat page
   * Layout: Sidebar (sessions) | Main (messages + input)
   */

  import { ref, onMounted } from 'vue'
  import { Menu, Settings } from 'lucide-vue-next'
  import { useAppStore } from '@/stores/modules/app'
  import { useAuthStore } from '@/stores/auth'
  import SessionList from '@/components/chat/SessionList.vue'
  import MessageList from '@/components/chat/MessageList.vue'
  import ChatInput from '@/components/chat/ChatInput.vue'

  const appStore = useAppStore()
  const authStore = useAuthStore()

  const chatInputRef = ref<InstanceType<typeof ChatInput> | null>(null)

  // Handle quick action from empty state
  function handleQuickAction(_action: string) {
    if (chatInputRef.value) {
      chatInputRef.value.focusInput()
    }
  }

  // Get user initials for avatar
  function getUserInitial() {
    const user = authStore.user
    if (user?.username) {
      return user.username.charAt(0).toUpperCase()
    }
    return 'U'
  }

  // Get display name
  function getDisplayName() {
    return authStore.user?.username || 'User'
  }

  function getDisplayEmail() {
    return authStore.user?.email || 'user@example.com'
  }

  // Initialize
  onMounted(async () => {
    // Fetch user info if authenticated but no user data
    if (authStore.isAuthenticated && !authStore.user) {
      try {
        await authStore.fetchUser()
      } catch (err) {
        console.error('Failed to fetch user:', err)
      }
    }
  })
</script>

<template>
  <div class="flex h-screen bg-background text-foreground font-sans overflow-hidden">
    <!-- Sidebar -->
    <aside
      class="flex flex-col border-r border-border bg-secondary transition-all duration-300"
      :class="appStore.sidebarCollapsed ? 'w-[60px]' : 'w-[260px]'"
    >
      <!-- Header -->
      <div class="flex items-center justify-between p-4 h-14 shrink-0 border-b border-border/40">
        <div
          v-if="!appStore.sidebarCollapsed"
          class="font-semibold text-base tracking-tight truncate ml-1"
        >
          Agentex
        </div>
        <button
          class="p-2 rounded-md hover:bg-white/5 text-muted-foreground hover:text-foreground transition-colors ml-auto"
          title="Toggle sidebar"
          @click="appStore.toggleSidebar"
        >
          <Menu class="w-5 h-5" :stroke-width="1.5" />
        </button>
      </div>

      <!-- Session List -->
      <SessionList :is-collapsed="appStore.sidebarCollapsed" class="flex-1" />

      <!-- User Footer -->
      <div class="p-2 m-2 border-t border-border pt-4">
        <div
          class="flex items-center gap-3 p-2 rounded-md hover:bg-accent/50 cursor-pointer transition-colors group"
        >
          <!-- User avatar -->
          <div
            class="w-8 h-8 rounded-full bg-indigo-500/10 flex items-center justify-center border border-indigo-500/20 text-indigo-400 font-mono text-xs ring-1 ring-transparent group-hover:ring-border transition-all"
          >
            {{ getUserInitial() }}
          </div>

          <!-- User info (when expanded) -->
          <div v-if="!appStore.sidebarCollapsed" class="flex-1 min-w-0">
            <div class="text-xs font-medium truncate group-hover:text-accent-foreground">
              {{ getDisplayName() }}
            </div>
            <div class="text-[10px] text-muted-foreground truncate">
              {{ getDisplayEmail() }}
            </div>
          </div>

          <!-- Settings link -->
          <router-link
            v-if="!appStore.sidebarCollapsed"
            to="/settings"
            class="text-muted-foreground hover:text-foreground p-1 rounded hover:bg-background"
            title="Settings"
          >
            <Settings class="w-4 h-4" :stroke-width="1.5" />
          </router-link>
        </div>
      </div>
    </aside>

    <!-- Main Content -->
    <main class="flex-1 flex flex-col min-w-0 bg-background relative h-full">
      <!-- Message List -->
      <MessageList class="flex-1" @action="handleQuickAction" />

      <!-- Chat Input -->
      <ChatInput ref="chatInputRef" />
    </main>
  </div>
</template>
