<script setup lang="ts">
  /**
   * MessageList Component
   * Displays the list of messages with auto-scroll and empty state
   */

  import { ref, computed, watch, nextTick, onMounted } from 'vue'
  import { useSessionStore } from '@/stores/session'
  import MessageItem from './MessageItem.vue'
  import ChatEmptyState from './ChatEmptyState.vue'

  const emit = defineEmits<{
    (e: 'action', action: string): void
  }>()

  const sessionStore = useSessionStore()

  const containerRef = ref<HTMLElement | null>(null)
  const shouldAutoScroll = ref(true)
  const showScrollButton = ref(false)

  // Current messages
  const messages = computed(() => sessionStore.currentMessages)
  const hasMessages = computed(() => messages.value.length > 0)
  const hasSession = computed(() => sessionStore.currentSession !== null)

  // Auto-scroll when new messages arrive or content updates
  watch(
    () => [messages.value.length, messages.value[messages.value.length - 1]?.content],
    () => {
      if (shouldAutoScroll.value) {
        scrollToBottom()
      }
    },
    { deep: true }
  )

  // Track scroll position to determine if we should auto-scroll
  function handleScroll() {
    if (!containerRef.value) return

    const { scrollTop, scrollHeight, clientHeight } = containerRef.value
    const distanceFromBottom = scrollHeight - scrollTop - clientHeight

    // If user is near bottom (within 100px), enable auto-scroll
    shouldAutoScroll.value = distanceFromBottom < 100

    // Show scroll button when far from bottom
    showScrollButton.value = distanceFromBottom > 300
  }

  // Scroll to bottom
  function scrollToBottom(smooth = true) {
    nextTick(() => {
      if (containerRef.value) {
        containerRef.value.scrollTo({
          top: containerRef.value.scrollHeight,
          behavior: smooth ? 'smooth' : 'auto'
        })
      }
    })
  }

  // Handle empty state action
  function handleAction(action: string) {
    emit('action', action)
  }

  // Initial scroll
  onMounted(() => {
    if (hasMessages.value) {
      scrollToBottom(false)
    }
  })
</script>

<template>
  <div class="relative flex-1 overflow-hidden">
    <!-- Message container -->
    <div
      ref="containerRef"
      class="h-full overflow-y-auto px-4 md:px-6 lg:px-8 scrollbar-thin"
      @scroll="handleScroll"
    >
      <!-- Empty state (no session or no messages) -->
      <template v-if="!hasSession || !hasMessages">
        <div class="flex items-center justify-center h-full">
          <ChatEmptyState @action="handleAction" />
        </div>
      </template>

      <!-- Messages list -->
      <template v-else>
        <div class="max-w-4xl mx-auto py-6 space-y-2">
          <TransitionGroup name="message" tag="div" class="space-y-1">
            <MessageItem v-for="message in messages" :key="message.id" :message="message" />
          </TransitionGroup>

          <!-- Typing indicator when streaming with no content -->
          <div
            v-if="sessionStore.isStreaming && !messages[messages.length - 1]?.content"
            class="flex items-center gap-3 py-4 px-4 text-muted-foreground"
          >
            <div
              class="w-8 h-8 rounded-lg bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 flex items-center justify-center"
            >
              <svg
                class="w-4 h-4 animate-spin"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  class="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  stroke-width="4"
                />
                <path
                  class="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                />
              </svg>
            </div>
            <div class="flex items-center gap-1">
              <span
                class="w-2 h-2 bg-current rounded-full animate-bounce"
                style="animation-delay: 0ms"
              />
              <span
                class="w-2 h-2 bg-current rounded-full animate-bounce"
                style="animation-delay: 150ms"
              />
              <span
                class="w-2 h-2 bg-current rounded-full animate-bounce"
                style="animation-delay: 300ms"
              />
            </div>
          </div>

          <!-- Bottom padding for scroll -->
          <div class="h-4" />
        </div>
      </template>
    </div>

    <!-- Scroll to bottom button -->
    <Transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="opacity-0 translate-y-4"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition duration-150 ease-in"
      leave-from-class="opacity-100 translate-y-0"
      leave-to-class="opacity-0 translate-y-4"
    >
      <button
        v-if="showScrollButton"
        class="absolute bottom-4 right-4 p-2 bg-secondary border border-border rounded-full shadow-lg hover:bg-accent transition-colors"
        title="Scroll to bottom"
        @click="scrollToBottom()"
      >
        <svg
          class="w-5 h-5 text-foreground"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          stroke-width="1.5"
        >
          <path stroke-linecap="round" stroke-linejoin="round" d="M19 14l-7 7m0 0l-7-7m7 7V3" />
        </svg>
      </button>
    </Transition>
  </div>
</template>

<style scoped>
  /* Message enter/leave transitions */
  .message-enter-active {
    transition: all 0.3s ease-out;
  }

  .message-leave-active {
    transition: all 0.2s ease-in;
  }

  .message-enter-from {
    opacity: 0;
    transform: translateY(10px);
  }

  .message-leave-to {
    opacity: 0;
    transform: translateX(-10px);
  }

  /* Scrollbar styling */
  .scrollbar-thin::-webkit-scrollbar {
    width: 6px;
  }

  .scrollbar-thin::-webkit-scrollbar-track {
    background: transparent;
  }

  .scrollbar-thin::-webkit-scrollbar-thumb {
    background: var(--border-default);
    border-radius: 3px;
  }

  .scrollbar-thin::-webkit-scrollbar-thumb:hover {
    background: var(--border-active);
  }

  /* Bounce animation adjustment */
  @keyframes bounce {
    0%,
    100% {
      transform: translateY(0);
    }
    50% {
      transform: translateY(-4px);
    }
  }
</style>
