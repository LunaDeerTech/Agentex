<script setup lang="ts">
  /**
   * MessageStream Component
   *
   * Displays a streaming message with typing indicator and tool call blocks.
   * Used for real-time display of agent responses.
   */

  import { computed, ref } from 'vue'
  import {
    Bot,
    Loader2,
    Wrench,
    CheckCircle2,
    XCircle,
    ChevronDown,
    ChevronRight
  } from 'lucide-vue-next'
  import type { ToolCall } from '@/composables/useAgentChat'
  import { renderMarkdown } from '@/lib/markdown'

  interface Props {
    content: string
    isStreaming?: boolean
    role?: 'assistant' | 'tool'
    toolCalls?: ToolCall[]
    stepName?: string | null
  }

  const props = withDefaults(defineProps<Props>(), {
    isStreaming: false,
    role: 'assistant',
    toolCalls: () => [],
    stepName: null
  })

  // Tool calls expansion state
  const expandedToolCalls = ref<Set<string>>(new Set())

  // Toggle tool call expansion
  function toggleToolCall(id: string) {
    if (expandedToolCalls.value.has(id)) {
      expandedToolCalls.value.delete(id)
    } else {
      expandedToolCalls.value.add(id)
    }
  }

  // Check if tool call is expanded
  function isToolCallExpanded(id: string): boolean {
    return expandedToolCalls.value.has(id)
  }

  // Format JSON for display
  function formatJson(str: string): string {
    try {
      const parsed = JSON.parse(str)
      return JSON.stringify(parsed, null, 2)
    } catch {
      return str
    }
  }

  // Render markdown content using markdown-it
  const renderedContent = computed(() => {
    if (!props.content) return ''
    return renderMarkdown(props.content)
  })

  // Step label mapping
  const stepLabels: Record<string, string> = {
    thinking: '思考中...',
    action: '执行工具...',
    observation: '观察结果...',
    final: '生成回复...'
  }

  // Get step label
  const stepLabel = computed(() => {
    if (!props.stepName) return null
    return stepLabels[props.stepName] || props.stepName
  })
</script>

<template>
  <div class="flex gap-4 py-4 px-4 rounded-xl bg-card/30 hover:bg-card/50 transition-colors">
    <!-- Avatar -->
    <div
      class="w-8 h-8 shrink-0 rounded-lg bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 flex items-center justify-center"
    >
      <Bot class="w-4 h-4" :stroke-width="1.5" />
    </div>

    <!-- Content area -->
    <div class="flex-1 min-w-0 space-y-3">
      <!-- Step indicator -->
      <div
        v-if="stepLabel && isStreaming"
        class="flex items-center gap-2 text-xs text-muted-foreground"
      >
        <Loader2 class="w-3 h-3 animate-spin" :stroke-width="1.5" />
        <span>{{ stepLabel }}</span>
      </div>

      <!-- Tool calls -->
      <div v-if="toolCalls.length > 0" class="space-y-2">
        <div
          v-for="toolCall in toolCalls"
          :key="toolCall.id"
          class="border border-border rounded-lg overflow-hidden"
        >
          <!-- Tool call header -->
          <button
            class="w-full flex items-center gap-2 px-3 py-2 bg-secondary/50 hover:bg-secondary/80 transition-colors text-left"
            @click="toggleToolCall(toolCall.id)"
          >
            <!-- Status icon -->
            <div
              class="w-5 h-5 rounded flex items-center justify-center"
              :class="{
                'bg-blue-500/10 text-blue-400': toolCall.status === 'running',
                'bg-green-500/10 text-green-400': toolCall.status === 'completed',
                'bg-red-500/10 text-red-400': toolCall.status === 'error',
                'bg-muted text-muted-foreground': toolCall.status === 'pending'
              }"
            >
              <Loader2
                v-if="toolCall.status === 'running'"
                class="w-3 h-3 animate-spin"
                :stroke-width="1.5"
              />
              <CheckCircle2
                v-else-if="toolCall.status === 'completed'"
                class="w-3 h-3"
                :stroke-width="1.5"
              />
              <XCircle
                v-else-if="toolCall.status === 'error'"
                class="w-3 h-3"
                :stroke-width="1.5"
              />
              <Wrench v-else class="w-3 h-3" :stroke-width="1.5" />
            </div>

            <!-- Tool name -->
            <span class="text-sm font-mono text-foreground">{{ toolCall.name }}</span>

            <!-- Status badge -->
            <span v-if="toolCall.status === 'running'" class="ml-auto text-xs text-blue-400">
              执行中
            </span>
            <span
              v-else-if="toolCall.status === 'completed'"
              class="ml-auto text-xs text-green-400"
            >
              完成
            </span>

            <!-- Expand icon -->
            <component
              :is="isToolCallExpanded(toolCall.id) ? ChevronDown : ChevronRight"
              class="w-4 h-4 text-muted-foreground"
              :stroke-width="1.5"
            />
          </button>

          <!-- Tool call details (expanded) -->
          <div v-if="isToolCallExpanded(toolCall.id)" class="px-3 py-2 space-y-2 bg-background/50">
            <!-- Arguments -->
            <div v-if="toolCall.arguments">
              <div class="text-xs text-muted-foreground mb-1">输入参数:</div>
              <pre class="text-xs bg-secondary/30 p-2 rounded overflow-x-auto font-mono">{{
                formatJson(toolCall.arguments)
              }}</pre>
            </div>

            <!-- Result -->
            <div v-if="toolCall.result">
              <div class="text-xs text-muted-foreground mb-1">执行结果:</div>
              <pre class="text-xs bg-secondary/30 p-2 rounded overflow-x-auto font-mono">{{
                formatJson(toolCall.result)
              }}</pre>
            </div>
          </div>
        </div>
      </div>

      <!-- Message content -->
      <div
        v-if="content"
        class="prose prose-invert prose-sm max-w-none text-foreground"
        v-html="renderedContent"
      />

      <!-- Typing indicator -->
      <div v-if="isStreaming && !content" class="flex items-center gap-1">
        <span
          class="w-2 h-2 bg-muted-foreground rounded-full animate-bounce"
          style="animation-delay: 0ms"
        />
        <span
          class="w-2 h-2 bg-muted-foreground rounded-full animate-bounce"
          style="animation-delay: 150ms"
        />
        <span
          class="w-2 h-2 bg-muted-foreground rounded-full animate-bounce"
          style="animation-delay: 300ms"
        />
      </div>

      <!-- Cursor when streaming with content -->
      <span
        v-if="isStreaming && content"
        class="inline-block w-0.5 h-4 bg-indigo-400 animate-pulse ml-0.5"
      />
    </div>
  </div>
</template>

<style scoped>
  /* Code block styling */
  :deep(.code-block) {
    @apply bg-secondary/50 rounded-lg p-3 overflow-x-auto my-2;
  }

  :deep(.code-block code) {
    @apply text-xs font-mono text-foreground;
  }

  :deep(.inline-code) {
    @apply bg-secondary/50 px-1.5 py-0.5 rounded text-xs font-mono text-accent;
  }

  /* Prose customization */
  :deep(.prose) {
    --tw-prose-body: var(--foreground);
    --tw-prose-headings: var(--foreground);
    --tw-prose-links: var(--primary);
    --tw-prose-code: var(--accent);
  }

  :deep(.prose p) {
    @apply my-1;
  }

  :deep(.prose strong) {
    @apply text-foreground;
  }

  :deep(.prose em) {
    @apply text-muted-foreground;
  }
</style>
