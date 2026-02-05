<script setup lang="ts">
  /**
   * ToolCallDisplay Component
   *
   * Enhanced tool call display with icon, collapsible JSON,
   * execution status, and timing information.
   */

  import { ref, computed, watch } from 'vue'
  import {
    Wrench,
    Loader2,
    CheckCircle2,
    XCircle,
    AlertCircle,
    ChevronDown,
    ChevronRight,
    Clock,
    Copy,
    Check,
    Database,
    Search,
    MessageSquare,
    Globe,
    Code
  } from 'lucide-vue-next'

  export interface ToolCallProps {
    id: string
    name: string
    arguments?: string | Record<string, unknown>
    result?: string | Record<string, unknown>
    status: 'pending' | 'running' | 'completed' | 'error'
    error?: string
    startTime?: number
    endTime?: number
    defaultExpanded?: boolean
  }

  const props = withDefaults(defineProps<ToolCallProps>(), {
    arguments: '',
    result: '',
    error: '',
    startTime: undefined,
    endTime: undefined,
    defaultExpanded: false
  })

  // Expansion states
  const isExpanded = ref(props.defaultExpanded)
  const isArgsExpanded = ref(true)
  const isResultExpanded = ref(true)

  // Copy state
  const argsCopied = ref(false)
  const resultCopied = ref(false)

  // Auto-expand when running
  watch(
    () => props.status,
    status => {
      if (status === 'running') {
        isExpanded.value = true
      }
    }
  )

  // Toggle expansion
  function toggle() {
    isExpanded.value = !isExpanded.value
  }

  // Get tool icon based on name
  function getToolIcon(toolName: string) {
    const name = toolName.toLowerCase()
    if (name.includes('search') || name.includes('query')) return Search
    if (name.includes('database') || name.includes('db') || name.includes('sql')) return Database
    if (name.includes('chat') || name.includes('message') || name.includes('send'))
      return MessageSquare
    if (name.includes('http') || name.includes('api') || name.includes('fetch')) return Globe
    if (name.includes('code') || name.includes('execute') || name.includes('run')) return Code
    if (name.includes('knowledge') || name.includes('retriev')) return Search
    return Wrench
  }

  // Format JSON for display
  function formatJson(value: string | Record<string, unknown>): string {
    if (!value) return '{}'
    if (typeof value === 'string') {
      try {
        const parsed = JSON.parse(value)
        return JSON.stringify(parsed, null, 2)
      } catch {
        return value
      }
    }
    return JSON.stringify(value, null, 2)
  }

  // Get raw value for copying
  function getRawValue(value: string | Record<string, unknown>): string {
    if (!value) return ''
    if (typeof value === 'string') return value
    return JSON.stringify(value)
  }

  // Computed duration
  const duration = computed(() => {
    if (props.status === 'running' && props.startTime) {
      return Date.now() - props.startTime
    }
    if (props.startTime && props.endTime) {
      return props.endTime - props.startTime
    }
    return null
  })

  // Format duration
  const formattedDuration = computed(() => {
    if (!duration.value) return null
    if (duration.value < 1000) {
      return `${duration.value}ms`
    }
    return `${(duration.value / 1000).toFixed(1)}s`
  })

  // Status color classes
  const statusClasses = computed(() => {
    switch (props.status) {
      case 'running':
        return 'bg-blue-500/10 text-blue-400 border-blue-500/30'
      case 'completed':
        return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
      case 'error':
        return 'bg-red-500/10 text-red-400 border-red-500/30'
      default:
        return 'bg-secondary text-muted-foreground border-border'
    }
  })

  // Header status classes
  const headerStatusClasses = computed(() => {
    switch (props.status) {
      case 'running':
        return 'border-blue-500/20'
      case 'completed':
        return 'border-emerald-500/20'
      case 'error':
        return 'border-red-500/20'
      default:
        return 'border-border/50'
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

  // Copy to clipboard
  async function copyArgs() {
    try {
      await navigator.clipboard.writeText(getRawValue(props.arguments!))
      argsCopied.value = true
      setTimeout(() => (argsCopied.value = false), 2000)
    } catch {
      console.error('Failed to copy')
    }
  }

  async function copyResult() {
    try {
      await navigator.clipboard.writeText(getRawValue(props.result!))
      resultCopied.value = true
      setTimeout(() => (resultCopied.value = false), 2000)
    } catch {
      console.error('Failed to copy')
    }
  }
</script>

<template>
  <div
    class="tool-call-display border rounded-xl overflow-hidden bg-card/30 backdrop-blur-sm transition-all duration-300"
    :class="headerStatusClasses"
  >
    <!-- Header -->
    <button
      class="w-full flex items-center gap-3 px-4 py-3 hover:bg-secondary/30 transition-colors text-left"
      @click="toggle"
    >
      <!-- Tool icon with status -->
      <div class="relative">
        <div
          class="w-8 h-8 rounded-lg flex items-center justify-center border transition-all duration-300"
          :class="statusClasses"
        >
          <Loader2 v-if="status === 'running'" class="w-4 h-4 animate-spin" :stroke-width="1.5" />
          <CheckCircle2 v-else-if="status === 'completed'" class="w-4 h-4" :stroke-width="1.5" />
          <XCircle v-else-if="status === 'error'" class="w-4 h-4" :stroke-width="1.5" />
          <component :is="getToolIcon(name)" v-else class="w-4 h-4" :stroke-width="1.5" />
        </div>

        <!-- Status pulse indicator -->
        <span
          v-if="status === 'running'"
          class="absolute -top-0.5 -right-0.5 w-2.5 h-2.5 bg-blue-500 rounded-full animate-ping"
        />
      </div>

      <!-- Tool info -->
      <div class="flex-1 min-w-0">
        <div class="flex items-center gap-2">
          <span class="text-sm font-medium text-foreground">调用工具</span>
          <code
            class="px-1.5 py-0.5 text-xs font-mono rounded bg-secondary/60 text-primary truncate max-w-[200px]"
          >
            {{ name }}
          </code>
        </div>
        <p class="text-[11px] text-muted-foreground mt-0.5">
          <template v-if="status === 'running'">正在执行...</template>
          <template v-else-if="status === 'completed'">执行成功</template>
          <template v-else-if="status === 'error'">{{ error || '执行失败' }}</template>
          <template v-else>等待执行</template>
        </p>
      </div>

      <!-- Status and duration -->
      <div class="flex items-center gap-2 shrink-0">
        <!-- Duration -->
        <div v-if="formattedDuration" class="flex items-center gap-1 text-xs text-muted-foreground">
          <Clock class="w-3 h-3" :stroke-width="1.5" />
          <span class="font-mono">{{ formattedDuration }}</span>
        </div>

        <!-- Status badge -->
        <span
          class="px-2 py-0.5 rounded-full text-[10px] font-medium"
          :class="{
            'bg-blue-500/10 text-blue-400': status === 'running',
            'bg-emerald-500/10 text-emerald-400': status === 'completed',
            'bg-red-500/10 text-red-400': status === 'error',
            'bg-secondary text-muted-foreground': status === 'pending'
          }"
        >
          {{ statusLabel }}
        </span>

        <!-- Expand icon -->
        <component
          :is="isExpanded ? ChevronDown : ChevronRight"
          class="w-4 h-4 text-muted-foreground transition-transform"
          :stroke-width="1.5"
        />
      </div>
    </button>

    <!-- Content -->
    <Transition
      enter-active-class="transition-all duration-300 ease-out"
      leave-active-class="transition-all duration-200 ease-in"
      enter-from-class="opacity-0 max-h-0"
      enter-to-class="opacity-100 max-h-[600px]"
      leave-from-class="opacity-100 max-h-[600px]"
      leave-to-class="opacity-0 max-h-0"
    >
      <div v-if="isExpanded" class="border-t border-border/30 overflow-hidden">
        <!-- Arguments section -->
        <div v-if="arguments" class="border-b border-border/20">
          <div
            class="w-full flex items-center gap-2 px-4 py-2 hover:bg-secondary/20 transition-colors text-left cursor-pointer"
            role="button"
            tabindex="0"
            @click="isArgsExpanded = !isArgsExpanded"
            @keydown.enter="isArgsExpanded = !isArgsExpanded"
            @keydown.space.prevent="isArgsExpanded = !isArgsExpanded"
          >
            <component
              :is="isArgsExpanded ? ChevronDown : ChevronRight"
              class="w-3 h-3 text-muted-foreground"
              :stroke-width="2"
            />
            <span class="text-xs font-medium text-muted-foreground">输入参数</span>
            <button
              class="ml-auto p-1 rounded hover:bg-secondary/50 text-muted-foreground hover:text-foreground transition-colors"
              title="复制参数"
              @click.stop="copyArgs"
            >
              <Check v-if="argsCopied" class="w-3 h-3 text-emerald-400" :stroke-width="2" />
              <Copy v-else class="w-3 h-3" :stroke-width="2" />
            </button>
          </div>

          <Transition
            enter-active-class="transition-all duration-200"
            leave-active-class="transition-all duration-150"
            enter-from-class="opacity-0 max-h-0"
            enter-to-class="opacity-100 max-h-[200px]"
            leave-from-class="opacity-100 max-h-[200px]"
            leave-to-class="opacity-0 max-h-0"
          >
            <div v-if="isArgsExpanded" class="px-4 pb-3 overflow-hidden">
              <pre
                class="p-3 rounded-lg bg-background/60 border border-border/30 text-xs font-mono text-muted-foreground overflow-x-auto max-h-[150px]"
              ><code>{{ formatJson(arguments) }}</code></pre>
            </div>
          </Transition>
        </div>

        <!-- Result section -->
        <div v-if="result || error">
          <div
            class="w-full flex items-center gap-2 px-4 py-2 hover:bg-secondary/20 transition-colors text-left cursor-pointer"
            role="button"
            tabindex="0"
            @click="isResultExpanded = !isResultExpanded"
            @keydown.enter="isResultExpanded = !isResultExpanded"
            @keydown.space.prevent="isResultExpanded = !isResultExpanded"
          >
            <component
              :is="isResultExpanded ? ChevronDown : ChevronRight"
              class="w-3 h-3 text-muted-foreground"
              :stroke-width="2"
            />
            <span class="text-xs font-medium text-muted-foreground">
              {{ error ? '错误信息' : '执行结果' }}
            </span>
            <button
              v-if="result && !error"
              class="ml-auto p-1 rounded hover:bg-secondary/50 text-muted-foreground hover:text-foreground transition-colors"
              title="复制结果"
              @click.stop="copyResult"
            >
              <Check v-if="resultCopied" class="w-3 h-3 text-emerald-400" :stroke-width="2" />
              <Copy v-else class="w-3 h-3" :stroke-width="2" />
            </button>
          </div>

          <Transition
            enter-active-class="transition-all duration-200"
            leave-active-class="transition-all duration-150"
            enter-from-class="opacity-0 max-h-0"
            enter-to-class="opacity-100 max-h-[200px]"
            leave-from-class="opacity-100 max-h-[200px]"
            leave-to-class="opacity-0 max-h-0"
          >
            <div v-if="isResultExpanded" class="px-4 pb-3 overflow-hidden">
              <!-- Error display -->
              <div
                v-if="error"
                class="p-3 rounded-lg bg-red-500/5 border border-red-500/20 flex items-start gap-2"
              >
                <AlertCircle class="w-4 h-4 text-red-400 shrink-0 mt-0.5" :stroke-width="1.5" />
                <p class="text-xs text-red-400">{{ error }}</p>
              </div>

              <!-- Result display -->
              <pre
                v-else
                class="p-3 rounded-lg bg-background/60 border border-border/30 text-xs font-mono text-muted-foreground overflow-x-auto max-h-[150px]"
              ><code>{{ formatJson(result) }}</code></pre>
            </div>
          </Transition>
        </div>

        <!-- Loading state for result -->
        <div
          v-if="status === 'running' && !result"
          class="px-4 py-3 flex items-center gap-2 text-muted-foreground"
        >
          <Loader2 class="w-3 h-3 animate-spin" :stroke-width="2" />
          <span class="text-xs">等待执行结果...</span>
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
  pre {
    margin: 0;
    white-space: pre-wrap;
    word-break: break-word;
  }

  code {
    font-family: ui-monospace, 'SF Mono', Monaco, 'Andale Mono', monospace;
  }
</style>
