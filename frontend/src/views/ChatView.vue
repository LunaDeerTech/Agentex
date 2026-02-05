<script setup lang="ts">
  import { ref } from 'vue'
  import { Send, Menu, Plus, Settings, Paperclip, ChevronDown } from 'lucide-vue-next'
  import { useSessionStore, useAppStore } from '@/stores'
  import ChatEmptyState from '@/components/chat/ChatEmptyState.vue'

  const sessionStore = useSessionStore()
  const appStore = useAppStore()
  const inputMessage = ref('')

  function handleSend() {
    if (!inputMessage.value.trim() || sessionStore.isStreaming) return
    console.log('Sending message:', inputMessage.value)
    inputMessage.value = ''
  }

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  function handleAction(action: string) {
    inputMessage.value = action
  }
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
          @click="appStore.toggleSidebar"
        >
          <Menu class="w-5 h-5" :stroke-width="1.5" />
        </button>
      </div>

      <!-- New Chat Button -->
      <div class="px-3 py-3">
        <button
          class="flex items-center gap-2 w-full p-2 text-sm rounded-md border border-border bg-card hover:bg-accent hover:text-accent-foreground transition-all duration-200 group text-left shadow-sm"
          :class="{ 'justify-center': appStore.sidebarCollapsed }"
        >
          <Plus
            class="w-4 h-4 text-muted-foreground group-hover:text-foreground"
            :stroke-width="1.5"
          />
          <span v-if="!appStore.sidebarCollapsed" class="text-sm font-medium"
            >New Conversation</span
          >
        </button>
      </div>

      <!-- Session List (Placeholder) -->
      <div class="flex-1 overflow-y-auto px-2 space-y-1">
        <div
          v-if="!appStore.sidebarCollapsed"
          class="text-xs font-medium text-muted-foreground px-3 py-2 mt-2"
        >
          Recent
        </div>
        <!-- Example items -->
        <!-- <div class="px-3 py-2 text-sm rounded-md hover:bg-accent/50 cursor-pointer truncate text-muted-foreground hover:text-foreground transition-colors">
          Project Planning
        </div> -->
        <div
          class="flex flex-col items-center justify-center py-10 text-muted-foreground text-sm text-center px-4"
          v-if="!appStore.sidebarCollapsed"
        >
          <span class="opacity-50 text-xs">No conversations yet</span>
        </div>
      </div>

      <!-- User Footer -->
      <div class="p-2 m-2 border-t border-border pt-4">
        <div
          class="flex items-center gap-3 p-2 rounded-md hover:bg-accent/50 cursor-pointer transition-colors group"
        >
          <div
            class="w-8 h-8 rounded-full bg-indigo-500/10 flex items-center justify-center border border-indigo-500/20 text-indigo-400 font-mono text-xs ring-1 ring-transparent group-hover:ring-border transition-all"
          >
            U
          </div>
          <div v-if="!appStore.sidebarCollapsed" class="flex-1 min-w-0">
            <div class="text-xs font-medium truncate group-hover:text-accent-foreground">User</div>
            <div class="text-[10px] text-muted-foreground truncate">user@example.com</div>
          </div>
          <router-link
            to="/settings"
            v-if="!appStore.sidebarCollapsed"
            class="text-muted-foreground hover:text-foreground p-1 rounded hover:bg-background"
          >
            <Settings class="w-4 h-4" :stroke-width="1.5" />
          </router-link>
        </div>
      </div>
    </aside>

    <!-- Main Content -->
    <main class="flex-1 flex flex-col min-w-0 bg-background relative h-full">
      <!-- Top Bar (Optional based on design doc 3.1 right side header) -->
      <!-- <header class="h-14 border-b border-border flex items-center justify-between px-6 shrink-0 z-10 bg-background/80 backdrop-blur-sm sticky top-0">
          <div class="text-sm font-medium flex items-center gap-2">
             <span class="text-muted-foreground">Model:</span>
             <span class="bg-secondary px-2 py-0.5 rounded text-xs">GPT-4o</span>
          </div>
      </header> -->

      <!-- Chat Messages -->
      <div class="flex-1 overflow-y-auto p-4 md:p-6 lg:p-8 flex flex-col items-center">
        <!-- Empty State -->
        <ChatEmptyState @action="handleAction" />
      </div>

      <!-- Input Area -->
      <div class="p-4 md:p-6 lg:p-8 max-w-4xl mx-auto w-full z-20">
        <div
          class="relative flex flex-col bg-secondary/40 backdrop-blur-sm border border-border/50 rounded-xl focus-within:border-primary/50 focus-within:ring-1 focus-within:ring-primary/20 transition-all shadow-lg hover:border-border/80"
        >
          <textarea
            v-model="inputMessage"
            class="w-full bg-transparent border-none text-sm p-4 min-h-[60px] max-h-[200px] resize-none focus:ring-0 placeholder:text-muted-foreground/70 font-sans leading-relaxed"
            placeholder="Type your message..."
            rows="1"
            @keydown="handleKeydown"
          ></textarea>

          <div class="flex items-center justify-between p-2 pl-4">
            <div class="flex items-center gap-2">
              <button
                class="p-2 text-muted-foreground hover:text-foreground hover:bg-white/5 rounded-lg transition-colors"
                title="Attach"
              >
                <Paperclip class="w-4 h-4" :stroke-width="1.5" />
              </button>
              <div class="h-4 w-px bg-border/50 mx-1"></div>
              <button
                class="flex items-center gap-1.5 px-2 py-1.5 text-xs font-medium text-muted-foreground hover:text-foreground hover:bg-white/5 rounded-lg transition-colors border border-transparent hover:border-border/50"
              >
                <span>GPT-4o</span>
                <ChevronDown class="w-3 h-3 opacity-50" />
              </button>
            </div>

            <button
              class="p-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-sm hover:shadow-md hover:shadow-primary/20"
              :disabled="!inputMessage.trim() || sessionStore.isStreaming"
              @click="handleSend"
            >
              <Send class="w-4 h-4" :stroke-width="1.5" />
            </button>
          </div>
        </div>
        <div class="text-center mt-3 text-[10px] text-muted-foreground/60 font-mono">
          Agentex can make mistakes. Consider checking important information.
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
  /* Custom Scrollbar for Webkit */
  ::-webkit-scrollbar {
    width: 6px;
    height: 6px;
  }
  ::-webkit-scrollbar-track {
    background: transparent;
  }
  ::-webkit-scrollbar-thumb {
    background: var(--color-border);
    border-radius: 3px;
  }
  ::-webkit-scrollbar-thumb:hover {
    background: var(--color-muted-foreground);
  }
</style>
