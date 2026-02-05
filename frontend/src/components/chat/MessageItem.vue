<script setup lang="ts">
  /**
   * MessageItem Component
   * Renders a single message with support for Markdown, code highlighting,
   * tool calls display, and thinking process visualization.
   */

  import { computed, ref } from 'vue'
  import { User, Bot, Copy, Check, AlertCircle, Loader2 } from 'lucide-vue-next'
  import type { LocalMessage, ToolCall, AgentStep } from '@/stores/session'
  import ThinkingProcess from './ThinkingProcess.vue'
  import ToolCallDisplay from './ToolCallDisplay.vue'
  import { renderMarkdown } from '@/lib/markdown'

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

  // Render markdown content using markdown-it
  const renderedContent = computed(() => {
    if (!props.message.content) return ''
    return renderMarkdown(props.message.content)
  })

  // Convert tool calls to ThinkingProcess format for display
  const hasToolCalls = computed(() => {
    return props.message.toolCalls && props.message.toolCalls.length > 0
  })

  const toolCallsForDisplay = computed(() => {
    if (!props.message.toolCalls) return []
    return props.message.toolCalls.map((tc: ToolCall) => ({
      id: tc.id,
      name: tc.name,
      arguments: tc.arguments,
      result: tc.result,
      status: tc.status
    }))
  })

  // Convert steps for ThinkingProcess component
  const hasSteps = computed(() => {
    return props.message.steps && props.message.steps.length > 0
  })

  const stepsForDisplay = computed(() => {
    if (!props.message.steps) return []
    return props.message.steps.map((s: AgentStep, idx: number) => ({
      id: `step-${idx}`,
      name: s.name,
      status: (s.status === 'running' ? 'running' : 'completed') as
        | 'pending'
        | 'running'
        | 'completed'
        | 'error',
      startTime: s.startTime,
      endTime: s.endTime,
      content: s.content // Pass the thinking content!
    }))
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
        <!-- Thinking Process (for assistant messages - shown ABOVE the answer) -->
        <ThinkingProcess
          v-if="isAssistant && (hasSteps || isStreaming)"
          :steps="stepsForDisplay"
          :is-active="isStreaming"
          :default-expanded="isStreaming"
          class="mb-3 w-full"
        />

        <!-- Tool Calls Display (shown above the answer) -->
        <div v-if="isAssistant && hasToolCalls" class="mb-3 space-y-2 w-full">
          <ToolCallDisplay
            v-for="toolCall in toolCallsForDisplay"
            :id="toolCall.id"
            :key="toolCall.id"
            :name="toolCall.name"
            :arguments="toolCall.arguments"
            :result="toolCall.result"
            :status="toolCall.status"
            :default-expanded="false"
          />
        </div>

        <!-- Message bubble (final answer) -->
        <div
          class="relative rounded-xl px-4 py-3"
          :class="[
            isUser
              ? 'bg-primary/10 border border-primary/20'
              : 'bg-secondary/50 border border-border/50',
            isError ? 'border-destructive/50' : ''
          ]"
        >
          <!-- Streaming indicator (when no content yet) -->
          <div
            v-if="isStreaming && !message.content"
            class="flex items-center gap-2 text-muted-foreground"
          >
            <Loader2 class="w-4 h-4 animate-spin" :stroke-width="1.5" />
            <span class="text-sm">生成回答中...</span>
          </div>

          <!-- Message content with markdown rendering -->
          <div
            v-else-if="message.content"
            class="prose prose-sm prose-invert max-w-none text-sm leading-relaxed markdown-content"
            v-html="renderedContent"
          />

          <!-- Streaming cursor -->
          <span
            v-if="isStreaming && message.content"
            class="inline-block w-0.5 h-4 ml-0.5 bg-primary animate-pulse"
          />

          <!-- Error indicator -->
          <div v-if="isError" class="flex items-center gap-2 mt-2 text-destructive text-xs">
            <AlertCircle class="w-3.5 h-3.5" :stroke-width="1.5" />
            <span>发送失败</span>
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
    white-space: pre;
  }

  :deep(.inline-code),
  :deep(code:not([class*='language-'])) {
    @apply px-1.5 py-0.5 rounded bg-secondary/80 text-primary font-mono text-xs;
  }

  /* Markdown content styling */
  :deep(.markdown-content) {
    line-height: 1.7;
  }

  :deep(.markdown-content h1),
  :deep(.markdown-content h2),
  :deep(.markdown-content h3),
  :deep(.markdown-content h4) {
    @apply font-semibold mt-4 mb-2;
  }

  :deep(.markdown-content h1) {
    @apply text-lg;
  }

  :deep(.markdown-content h2) {
    @apply text-base;
  }

  :deep(.markdown-content h3) {
    @apply text-sm font-semibold;
  }

  :deep(.markdown-content ul),
  :deep(.markdown-content ol) {
    @apply pl-5 my-2;
  }

  :deep(.markdown-content ul) {
    list-style-type: disc;
  }

  :deep(.markdown-content ol) {
    list-style-type: decimal;
  }

  :deep(.markdown-content li) {
    @apply my-1;
  }

  :deep(.markdown-content blockquote) {
    @apply border-l-2 border-primary/50 pl-4 my-3 text-muted-foreground italic;
  }

  :deep(.markdown-content table) {
    @apply w-full my-3 border-collapse;
  }

  :deep(.markdown-content th),
  :deep(.markdown-content td) {
    @apply border border-border px-3 py-2 text-left;
  }

  :deep(.markdown-content th) {
    @apply bg-secondary/50 font-semibold;
  }

  :deep(.markdown-content hr) {
    @apply my-4 border-border;
  }

  :deep(.markdown-content a) {
    @apply text-primary hover:underline;
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
