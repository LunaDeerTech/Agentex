<script setup lang="ts">
  /**
   * SessionList Component
   * Displays the list of chat sessions with search and management
   */

  import { ref, computed, onMounted } from 'vue'
  import { Plus, Search, X, Loader2 } from 'lucide-vue-next'
  import { useSessionStore } from '@/stores/session'
  import SessionItem from './SessionItem.vue'
  import type { Session } from '@/api/session'

  interface Props {
    isCollapsed?: boolean
  }

  const { isCollapsed = false } = defineProps<Props>()

  const sessionStore = useSessionStore()

  const searchQuery = ref('')
  const showSearch = ref(false)
  const isCreating = ref(false)

  // Rename dialog state
  const renameDialog = ref({
    show: false,
    session: null as Session | null,
    newTitle: ''
  })

  // Delete dialog state
  const deleteDialog = ref({
    show: false,
    session: null as Session | null
  })

  // Filtered sessions based on search
  const filteredSessions = computed(() => {
    if (!searchQuery.value.trim()) {
      return sessionStore.sortedSessions
    }

    const query = searchQuery.value.toLowerCase()
    return sessionStore.sortedSessions.filter(session =>
      (session.title || 'New Conversation').toLowerCase().includes(query)
    )
  })

  // Group sessions by date
  const groupedSessions = computed(() => {
    const groups: { label: string; sessions: Session[] }[] = []
    const today = new Date()
    const yesterday = new Date(today)
    yesterday.setDate(yesterday.getDate() - 1)
    const weekAgo = new Date(today)
    weekAgo.setDate(weekAgo.getDate() - 7)

    const todaySessions: Session[] = []
    const yesterdaySessions: Session[] = []
    const weekSessions: Session[] = []
    const olderSessions: Session[] = []

    filteredSessions.value.forEach(session => {
      const date = new Date(session.updated_at)
      if (isSameDay(date, today)) {
        todaySessions.push(session)
      } else if (isSameDay(date, yesterday)) {
        yesterdaySessions.push(session)
      } else if (date > weekAgo) {
        weekSessions.push(session)
      } else {
        olderSessions.push(session)
      }
    })

    if (todaySessions.length) groups.push({ label: 'Today', sessions: todaySessions })
    if (yesterdaySessions.length) groups.push({ label: 'Yesterday', sessions: yesterdaySessions })
    if (weekSessions.length) groups.push({ label: 'This Week', sessions: weekSessions })
    if (olderSessions.length) groups.push({ label: 'Older', sessions: olderSessions })

    return groups
  })

  function isSameDay(d1: Date, d2: Date): boolean {
    return (
      d1.getFullYear() === d2.getFullYear() &&
      d1.getMonth() === d2.getMonth() &&
      d1.getDate() === d2.getDate()
    )
  }

  // Actions
  async function handleCreateSession() {
    if (isCreating.value) return

    isCreating.value = true
    try {
      await sessionStore.createSession({
        title: undefined, // Will be auto-generated or set on first message
        agent_type: 'react'
      })
    } catch (err) {
      console.error('Failed to create session:', err)
    } finally {
      isCreating.value = false
    }
  }

  function handleSelectSession(session: Session) {
    sessionStore.selectSession(session.id)
  }

  function handleRenameSession(session: Session) {
    renameDialog.value = {
      show: true,
      session,
      newTitle: session.title || ''
    }
  }

  async function confirmRename() {
    if (!renameDialog.value.session || !renameDialog.value.newTitle.trim()) return

    try {
      await sessionStore.updateSession(renameDialog.value.session.id, {
        title: renameDialog.value.newTitle.trim()
      })
      renameDialog.value.show = false
    } catch (err) {
      console.error('Failed to rename session:', err)
    }
  }

  function handleDeleteSession(session: Session) {
    deleteDialog.value = {
      show: true,
      session
    }
  }

  async function confirmDelete() {
    if (!deleteDialog.value.session) return

    try {
      await sessionStore.deleteSession(deleteDialog.value.session.id)
      deleteDialog.value.show = false
    } catch (err) {
      console.error('Failed to delete session:', err)
    }
  }

  function toggleSearch() {
    showSearch.value = !showSearch.value
    if (!showSearch.value) {
      searchQuery.value = ''
    }
  }

  // Load sessions on mount
  onMounted(async () => {
    try {
      await sessionStore.fetchSessions()
    } catch (err) {
      console.error('Failed to load sessions:', err)
    }
  })
</script>

<template>
  <div class="flex flex-col h-full">
    <!-- New Chat Button -->
    <div class="px-3 py-3">
      <button
        class="flex items-center gap-2 w-full p-2 text-sm rounded-md border border-border bg-card hover:bg-accent hover:text-accent-foreground transition-all duration-200 group text-left shadow-sm disabled:opacity-50"
        :class="{ 'justify-center': isCollapsed }"
        :disabled="isCreating"
        @click="handleCreateSession"
      >
        <Loader2 v-if="isCreating" class="w-4 h-4 animate-spin" :stroke-width="1.5" />
        <Plus
          v-else
          class="w-4 h-4 text-muted-foreground group-hover:text-foreground"
          :stroke-width="1.5"
        />
        <span v-if="!isCollapsed" class="text-sm font-medium">New Conversation</span>
      </button>
    </div>

    <!-- Search (optional, visible when expanded) -->
    <div v-if="!isCollapsed && showSearch" class="px-3 pb-2">
      <div class="relative">
        <Search
          class="absolute left-2.5 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground"
          :stroke-width="1.5"
        />
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search conversations..."
          class="w-full h-8 pl-8 pr-8 text-sm bg-secondary/50 border border-border rounded-md focus:outline-none focus:border-border-active focus:ring-1 focus:ring-primary/20 placeholder:text-muted-foreground/50"
        />
        <button
          v-if="searchQuery"
          class="absolute right-2 top-1/2 -translate-y-1/2 p-0.5 hover:bg-white/10 rounded"
          @click="searchQuery = ''"
        >
          <X class="w-3 h-3 text-muted-foreground" :stroke-width="1.5" />
        </button>
      </div>
    </div>

    <!-- Session List -->
    <div class="flex-1 overflow-y-auto px-2 space-y-1 scrollbar-thin">
      <!-- Loading state -->
      <div
        v-if="sessionStore.isLoading && !sessionStore.sessions.length"
        class="flex items-center justify-center py-10"
      >
        <Loader2 class="w-5 h-5 animate-spin text-muted-foreground" :stroke-width="1.5" />
      </div>

      <!-- Empty state -->
      <div
        v-else-if="!filteredSessions.length"
        class="flex flex-col items-center justify-center py-10 text-muted-foreground text-sm text-center px-4"
      >
        <template v-if="searchQuery">
          <span class="opacity-50 text-xs">No conversations found</span>
        </template>
        <template v-else>
          <span v-if="!isCollapsed" class="opacity-50 text-xs">No conversations yet</span>
        </template>
      </div>

      <!-- Session groups -->
      <template v-else>
        <div v-for="group in groupedSessions" :key="group.label" class="space-y-0.5">
          <!-- Group label -->
          <div
            v-if="!isCollapsed"
            class="text-xs font-medium text-muted-foreground px-3 py-2 mt-2 first:mt-0"
          >
            {{ group.label }}
          </div>

          <!-- Sessions -->
          <SessionItem
            v-for="session in group.sessions"
            :key="session.id"
            :session="session"
            :is-active="sessionStore.currentSessionId === session.id"
            :is-collapsed="isCollapsed"
            @select="handleSelectSession"
            @rename="handleRenameSession"
            @delete="handleDeleteSession"
          />
        </div>
      </template>
    </div>

    <!-- Search toggle (at bottom, optional) -->
    <div
      v-if="!isCollapsed && sessionStore.sessions.length > 5"
      class="px-3 py-2 border-t border-border/40"
    >
      <button
        class="flex items-center gap-2 w-full p-2 text-xs text-muted-foreground hover:text-foreground rounded hover:bg-white/5 transition-colors"
        @click="toggleSearch"
      >
        <Search class="w-3.5 h-3.5" :stroke-width="1.5" />
        <span>{{ showSearch ? 'Hide search' : 'Search conversations' }}</span>
      </button>
    </div>

    <!-- Rename Dialog -->
    <Teleport to="body">
      <Transition
        enter-active-class="transition duration-150 ease-out"
        enter-from-class="opacity-0"
        enter-to-class="opacity-100"
        leave-active-class="transition duration-100 ease-in"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
      >
        <div
          v-if="renameDialog.show"
          class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
          @click.self="renameDialog.show = false"
        >
          <div class="bg-card border border-border rounded-xl p-6 w-full max-w-md shadow-2xl">
            <h3 class="text-lg font-semibold mb-4">Rename Conversation</h3>
            <input
              v-model="renameDialog.newTitle"
              type="text"
              placeholder="Enter new title..."
              class="w-full h-10 px-3 text-sm bg-secondary/50 border border-border rounded-md focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/20"
              @keydown.enter="confirmRename"
            />
            <div class="flex justify-end gap-3 mt-6">
              <button
                class="px-4 py-2 text-sm text-muted-foreground hover:text-foreground rounded-md hover:bg-white/5 transition-colors"
                @click="renameDialog.show = false"
              >
                Cancel
              </button>
              <button
                class="px-4 py-2 text-sm bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors disabled:opacity-50"
                :disabled="!renameDialog.newTitle.trim()"
                @click="confirmRename"
              >
                Save
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- Delete Dialog -->
    <Teleport to="body">
      <Transition
        enter-active-class="transition duration-150 ease-out"
        enter-from-class="opacity-0"
        enter-to-class="opacity-100"
        leave-active-class="transition duration-100 ease-in"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
      >
        <div
          v-if="deleteDialog.show"
          class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
          @click.self="deleteDialog.show = false"
        >
          <div class="bg-card border border-border rounded-xl p-6 w-full max-w-md shadow-2xl">
            <h3 class="text-lg font-semibold mb-2">Delete Conversation</h3>
            <p class="text-sm text-muted-foreground mb-6">
              Are you sure you want to delete "{{
                deleteDialog.session?.title || 'New Conversation'
              }}"? This action cannot be undone.
            </p>
            <div class="flex justify-end gap-3">
              <button
                class="px-4 py-2 text-sm text-muted-foreground hover:text-foreground rounded-md hover:bg-white/5 transition-colors"
                @click="deleteDialog.show = false"
              >
                Cancel
              </button>
              <button
                class="px-4 py-2 text-sm bg-destructive text-destructive-foreground rounded-md hover:bg-destructive/90 transition-colors"
                @click="confirmDelete"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<style scoped>
  .scrollbar-thin::-webkit-scrollbar {
    width: 4px;
  }

  .scrollbar-thin::-webkit-scrollbar-track {
    background: transparent;
  }

  .scrollbar-thin::-webkit-scrollbar-thumb {
    background: var(--border-default);
    border-radius: 2px;
  }

  .scrollbar-thin::-webkit-scrollbar-thumb:hover {
    background: var(--border-active);
  }
</style>
