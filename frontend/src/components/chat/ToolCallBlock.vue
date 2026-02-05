<script setup lang="ts">
  /**
   * ToolCallBlock Component
   *
   * Displays a tool call with its arguments and result in a collapsible block.
   * Used within message streams to show agent tool interactions.
   */

  import { ref, computed } from 'vue'
  import {
    Wrench,
    Loader2,
    CheckCircle2,
    XCircle,
    ChevronDown,
    ChevronRight,
    Clock
  } from 'lucide-vue-next'

  interface Props {
    id: string
    name: string
    arguments?: string
    result?: string
    status: 'pending' | 'running' | 'completed' | 'error'
    error?: string
    duration?: number
    defaultExpanded?: boolean
  }

  const props = withDefaults(defineProps<Props>(), {
    arguments: '',
    result: '',
    error: '',
    duration: undefined,
    defaultExpanded: false
  })

  // Expansion state
  const isExpanded = ref(props.defaultExpanded)

  // Toggle expansion
  function toggle() {
    isExpanded.value = !isExpanded.value
  }

  // Format JSON for display
  function formatJson(str: string): string {
    if (!str) return '{}'
    try {
      const parsed = JSON.parse(str)
      return JSON.stringify(parsed, null, 2)
    } catch {
      return str
    }
  }

  // Format duration
  const formattedDuration = computed(() => {
    if (!props.duration) return null
    if (props.duration < 1000) {
      return `${props.duration}ms`
    }
    return `${(props.duration / 1000).toFixed(1)}s`
  })

  // Status color classes
  const statusClasses = computed(() => {
    switch (props.status) {
      case 'running':
        return 'bg-blue-500/10 text-blue-400 border-blue-500/20'
      case 'completed':
        return 'bg-green-500/10 text-green-400 border-green-500/20'
      case 'error':
        return 'bg-red-500/10 text-red-400 border-red-500/20'
      default:
        return 'bg-muted text-muted-foreground border-border'
    }
  })

  // Status label
  const statusLabel = computed(() => {
    switch (props.status) {
      case 'running':
        return '执行中'
      case 'completed':
        return '完成'
      case 'error':
        return '失败'
      default:
        return '等待'
    }
  })
</script>

<template>
  <div class="border border-border rounded-lg overflow-hidden bg-card/30">
    <!-- Header -->
    <button
      class="w-full flex items-center gap-3 px-4 py-3 hover:bg-secondary/50 transition-colors text-left"
      @click="toggle"
    >
      <!-- Status icon -->
      <div
        class="w-6 h-6 rounded-md flex items-center justify-center border"
        :class="statusClasses"
      >
        <Loader2 v-if="status === 'running'" class="w-3.5 h-3.5 animate-spin" :stroke-width="1.5" />
        <CheckCircle2 v-else-if="status === 'completed'" class="w-3.5 h-3.5" :stroke-width="1.5" />
        <XCircle v-else-if="status === 'error'" class="w-3.5 h-3.5" :stroke-width="1.5" />
        <Wrench v-else class="w-3.5 h-3.5" :stroke-width="1.5" />
      </div>

      <!-- Tool info -->
      <div class="flex-1 min-w-0">
        <div class="flex items-center gap-2">
          <span class="text-sm font-medium text-foreground">调用工具</span>
          <span class="text-sm font-mono text-accent truncate">{{ name }}</span>
        </div>
      </div>

      <!-- Status and duration -->
      <div class="flex items-center gap-3 text-xs">
        <span
          v-if="formattedDuration && status === 'completed'"
          class="flex items-center gap-1 text-muted-foreground"
        >
          <Clock class="w-3 h-3" :stroke-width="1.5" />
          {{ formattedDuration }}
        </span>
        <span
          class="px-2 py-0.5 rounded-full text-xs"
          :class="{
            'bg-blue-500/10 text-blue-400': status === 'running',
            'bg-green-500/10 text-green-400': status === 'completed',
            'bg-red-500/10 text-red-400': status === 'error',
            'bg-muted text-muted-foreground': status === 'pending'
          }"
        >
          {{ statusLabel }}
        </span>
      </div>

      <!-- Expand icon -->
      <component
        :is="isExpanded ? ChevronDown : ChevronRight"
        class="w-4 h-4 text-muted-foreground shrink-0"
        :stroke-width="1.5"
      />
    </button>

    <!-- Details (expanded) -->
    <Transition
      enter-active-class="transition-all duration-200 ease-out"
      enter-from-class="opacity-0 max-h-0"
      enter-to-class="opacity-100 max-h-[500px]"
      leave-active-class="transition-all duration-150 ease-in"
      leave-from-class="opacity-100 max-h-[500px]"
      leave-to-class="opacity-0 max-h-0"
    >
      <div v-if="isExpanded" class="px-4 py-3 space-y-3 border-t border-border bg-background/30">
        <!-- Arguments -->
        <div>
          <div class="flex items-center gap-2 mb-1.5">
            <span class="text-xs font-medium text-muted-foreground uppercase tracking-wide">
              输入参数
            </span>
          </div>
          <pre
            class="text-xs bg-secondary/30 p-3 rounded-md overflow-x-auto font-mono text-foreground"
            >{{ formatJson(arguments) }}</pre
          >
        </div>

        <!-- Result -->
        <div v-if="result || error">
          <div class="flex items-center gap-2 mb-1.5">
            <span class="text-xs font-medium text-muted-foreground uppercase tracking-wide">
              {{ error ? '错误信息' : '执行结果' }}
            </span>
          </div>
          <pre
            class="text-xs p-3 rounded-md overflow-x-auto font-mono"
            :class="
              error
                ? 'bg-red-500/5 text-red-400 border border-red-500/20'
                : 'bg-secondary/30 text-foreground'
            "
            >{{ error || formatJson(result) }}</pre
          >
        </div>

        <!-- Loading state for result -->
        <div
          v-else-if="status === 'running'"
          class="flex items-center gap-2 text-xs text-muted-foreground"
        >
          <Loader2 class="w-3 h-3 animate-spin" :stroke-width="1.5" />
          <span>正在执行...</span>
        </div>
      </div>
    </Transition>
  </div>
</template>
