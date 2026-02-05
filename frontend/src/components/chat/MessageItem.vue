<script setup lang="ts">
  /**
   * MessageItem Component
   * Renders a single message with support for Markdown and code highlighting
   */

  import { computed, ref } from 'vue'
  import { User, Bot, Copy, Check, AlertCircle, Loader2 } from 'lucide-vue-next'
  import type { LocalMessage } from '@/stores/session'

  interface Props {
    message: LocalMessage
  }

  const props = defineProps<Props>()

  const copied = ref(false)

  // Format timestamp
  const formattedTime = computed(() => {
    const date = new Date(props.message.created_at)
    return date.toLocaleTimeString(undefined, {
      hour: '2-digit',
      minute: '2-digit'
    })
  })

  // Check if message is from user
  const isUser = computed(() => props.message.role === 'user')
  const isAssistant = computed(() => props.message.role === 'assistant')
  const isSystem = computed(() => props.message.role === 'system')

  // Message status
  const isPending = computed(() => props.message.status === 'pending')
  const isStreaming = computed(() => props.message.status === 'streaming')
  const isError = computed(() => props.message.status === 'error')

  // Parse markdown content (basic implementation)
  // In production, use a proper markdown library like marked or markdown-it
  const renderedContent = computed(() => {
    let content = props.message.content

    // Escape HTML
    content = content.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')

    // Code blocks
    content = content.replace(/```(\w*)\n([\s\S]*?)```/g, (_match, lang, code) => {
      return `<pre class="code-block"><code class="language-${lang || 'text'}">${code.trim()}</code></pre>`
    })

    // Inline code
    content = content.replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>')

    // Bold
    content = content.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')

    // Italic
    content = content.replace(/\*([^*]+)\*/g, '<em>$1</em>')

    // Links
    content = content.replace(
      /\[([^\]]+)\]\(([^)]+)\)/g,
      '<a href="$2" target="_blank" rel="noopener noreferrer" class="text-primary hover:underline">$1</a>'
    )

    // Line breaks
    content = content.replace(/\n/g, '<br>')

    return content
  })

  // Copy message content
  async function copyContent() {
    try {
      await navigator.clipboard.writeText(props.message.content)
      copied.value = true
      setTimeout(() => {
        copied.value = false
      }, 2000)
    } catch (err) {
      console.error('Failed to copy:', err)
    }
  }
</script>

<template>
  <div
    class="group flex gap-4 py-4 px-4 rounded-xl transition-colors"
    :class="{
      'flex-row-reverse': isUser,
      'bg-card/30 hover:bg-card/50': isAssistant,
      'justify-center': isSystem
    }"
  >
    <!-- System message -->
    <template v-if="isSystem">
      <div class="text-xs text-muted-foreground bg-secondary/50 px-3 py-1.5 rounded-full">
        {{ message.content }}
      </div>
    </template>

    <!-- User/Assistant message -->
    <template v-else>
      <!-- Avatar -->
      <div
        class="shrink-0 w-8 h-8 rounded-lg flex items-center justify-center"
        :class="
          isUser
            ? 'bg-primary/10 text-primary border border-primary/20'
            : 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/20'
        "
      >
        <User v-if="isUser" class="w-4 h-4" :stroke-width="1.5" />
        <Bot v-else class="w-4 h-4" :stroke-width="1.5" />
      </div>

      <!-- Content -->
      <div class="flex-1 min-w-0 max-w-[85%]" :class="{ 'flex flex-col items-end': isUser }">
        <!-- Message bubble -->
        <div
          class="relative rounded-xl px-4 py-3"
          :class="[
            isUser
              ? 'bg-primary/10 border border-primary/20'
              : 'bg-secondary/50 border border-border/50',
            isError ? 'border-destructive/50' : ''
          ]"
        >
          <!-- Streaming indicator -->
          <div
            v-if="isStreaming && !message.content"
            class="flex items-center gap-2 text-muted-foreground"
          >
            <Loader2 class="w-4 h-4 animate-spin" :stroke-width="1.5" />
            <span class="text-sm">Thinking...</span>
          </div>

          <!-- Message content -->
          <div
            v-else
            class="prose prose-sm prose-invert max-w-none text-sm leading-relaxed"
            v-html="renderedContent"
          />

          <!-- Streaming cursor -->
          <span
            v-if="isStreaming && message.content"
            class="inline-block w-2 h-4 ml-0.5 bg-primary animate-pulse"
          />

          <!-- Error indicator -->
          <div v-if="isError" class="flex items-center gap-2 mt-2 text-destructive text-xs">
            <AlertCircle class="w-3.5 h-3.5" :stroke-width="1.5" />
            <span>Failed to send</span>
          </div>
        </div>

        <!-- Footer: time and actions -->
        <div class="flex items-center gap-2 mt-1.5 px-1" :class="{ 'flex-row-reverse': isUser }">
          <!-- Timestamp -->
          <span class="text-[10px] text-muted-foreground/60 font-mono">
            {{ formattedTime }}
          </span>

          <!-- Pending indicator -->
          <Loader2
            v-if="isPending"
            class="w-3 h-3 animate-spin text-muted-foreground/60"
            :stroke-width="1.5"
          />

          <!-- Copy button -->
          <button
            v-if="!isPending && !isStreaming && message.content"
            class="p-1 rounded opacity-0 group-hover:opacity-100 hover:bg-white/10 text-muted-foreground hover:text-foreground transition-all"
            :title="copied ? 'Copied!' : 'Copy message'"
            @click="copyContent"
          >
            <Check v-if="copied" class="w-3.5 h-3.5 text-success" :stroke-width="1.5" />
            <Copy v-else class="w-3.5 h-3.5" :stroke-width="1.5" />
          </button>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
  @reference "../../styles/variables.css";

  /* Code block styling */
  :deep(.code-block) {
    @apply my-3 p-4 rounded-lg bg-background/80 border border-border overflow-x-auto font-mono text-xs;
  }

  :deep(.code-block code) {
    color: var(--text-secondary);
  }

  :deep(.inline-code) {
    @apply px-1.5 py-0.5 rounded bg-secondary/80 text-primary font-mono text-xs;
  }

  /* Prose adjustments for dark theme */
  :deep(.prose) {
    --tw-prose-body: var(--text-primary);
    --tw-prose-headings: var(--text-primary);
    --tw-prose-bold: var(--text-primary);
    --tw-prose-links: var(--color-accent);
    --tw-prose-code: var(--color-accent);
  }

  :deep(.prose p) {
    @apply my-1.5;
  }

  :deep(.prose p:first-child) {
    @apply mt-0;
  }

  :deep(.prose p:last-child) {
    @apply mb-0;
  }
</style>
