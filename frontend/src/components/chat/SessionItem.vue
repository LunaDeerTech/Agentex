<script setup lang="ts">
  /**
   * SessionItem Component
   * Displays a single session in the sidebar list
   */

  import { computed, ref } from 'vue'
  import { MessageSquare, MoreHorizontal, Pencil, Trash2 } from 'lucide-vue-next'
  import type { Session } from '@/api/session'

  interface Props {
    session: Session
    isActive?: boolean
    isCollapsed?: boolean
  }

  const props = withDefaults(defineProps<Props>(), {
    isActive: false,
    isCollapsed: false
  })

  const emit = defineEmits<{
    (e: 'select', session: Session): void
    (e: 'rename', session: Session): void
    (e: 'delete', session: Session): void
  }>()

  const showMenu = ref(false)
  const menuRef = ref<HTMLElement | null>(null)

  // Format relative time
  const relativeTime = computed(() => {
    const date = new Date(props.session.updated_at)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / (1000 * 60))
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins}m ago`
    if (diffHours < 24) return `${diffHours}h ago`
    if (diffDays < 7) return `${diffDays}d ago`
    return date.toLocaleDateString()
  })

  // Display title
  const displayTitle = computed(() => {
    return props.session.title || 'New Conversation'
  })

  // Agent type label
  const agentTypeLabel = computed(() => {
    const types: Record<string, string> = {
      react: 'ReAct',
      agentic_rag: 'RAG',
      plan_execute: 'Plan'
    }
    return types[props.session.agent_type] || props.session.agent_type
  })

  function handleClick() {
    emit('select', props.session)
  }

  function handleContextMenu(e: MouseEvent) {
    e.preventDefault()
    showMenu.value = true
  }

  function handleMenuClick(e: MouseEvent) {
    e.stopPropagation()
    showMenu.value = !showMenu.value
  }

  function handleRename() {
    showMenu.value = false
    emit('rename', props.session)
  }

  function handleDelete() {
    showMenu.value = false
    emit('delete', props.session)
  }

  // Close menu when clicking outside
  function handleClickOutside(e: MouseEvent) {
    if (menuRef.value && !menuRef.value.contains(e.target as Node)) {
      showMenu.value = false
    }
  }

  // Add click outside listener when menu opens
  import { watch, onUnmounted } from 'vue'

  watch(showMenu, open => {
    if (open) {
      document.addEventListener('click', handleClickOutside)
    } else {
      document.removeEventListener('click', handleClickOutside)
    }
  })

  onUnmounted(() => {
    document.removeEventListener('click', handleClickOutside)
  })
</script>

<template>
  <div
    class="group relative flex items-center gap-2 px-3 py-2.5 rounded-lg cursor-pointer transition-all duration-150"
    :class="[
      isActive
        ? 'bg-accent/60 text-foreground border border-border/50'
        : 'hover:bg-accent/30 text-muted-foreground hover:text-foreground border border-transparent'
    ]"
    @click="handleClick"
    @contextmenu="handleContextMenu"
  >
    <!-- Icon (collapsed state) -->
    <div v-if="isCollapsed" class="w-8 h-8 flex items-center justify-center" :title="displayTitle">
      <MessageSquare class="w-4 h-4" :stroke-width="1.5" />
    </div>

    <!-- Content (expanded state) -->
    <template v-else>
      <!-- Icon -->
      <div class="shrink-0">
        <MessageSquare class="w-4 h-4 opacity-50" :stroke-width="1.5" />
      </div>

      <!-- Title and meta -->
      <div class="flex-1 min-w-0">
        <div class="text-sm font-medium truncate">
          {{ displayTitle }}
        </div>
        <div class="flex items-center gap-2 text-xs text-muted-foreground mt-0.5">
          <span>{{ relativeTime }}</span>
          <span class="opacity-50">·</span>
          <span class="px-1 py-0.5 rounded text-[10px] bg-secondary/50">
            {{ agentTypeLabel }}
          </span>
        </div>
      </div>

      <!-- More button -->
      <button
        ref="menuRef"
        class="shrink-0 p-1 rounded opacity-0 group-hover:opacity-100 hover:bg-white/10 transition-opacity"
        @click="handleMenuClick"
      >
        <MoreHorizontal class="w-4 h-4" :stroke-width="1.5" />
      </button>

      <!-- Context Menu -->
      <Transition
        enter-active-class="transition duration-100 ease-out"
        enter-from-class="transform scale-95 opacity-0"
        enter-to-class="transform scale-100 opacity-100"
        leave-active-class="transition duration-75 ease-in"
        leave-from-class="transform scale-100 opacity-100"
        leave-to-class="transform scale-95 opacity-0"
      >
        <div
          v-if="showMenu"
          class="absolute right-0 top-full mt-1 z-50 min-w-[140px] rounded-lg border border-border bg-popover shadow-lg py-1"
        >
          <button
            class="flex items-center gap-2 w-full px-3 py-2 text-sm text-left hover:bg-accent transition-colors"
            @click="handleRename"
          >
            <Pencil class="w-4 h-4 opacity-60" :stroke-width="1.5" />
            <span>Rename</span>
          </button>
          <button
            class="flex items-center gap-2 w-full px-3 py-2 text-sm text-left text-destructive hover:bg-destructive/10 transition-colors"
            @click="handleDelete"
          >
            <Trash2 class="w-4 h-4 opacity-60" :stroke-width="1.5" />
            <span>Delete</span>
          </button>
        </div>
      </Transition>
    </template>
  </div>
</template>
