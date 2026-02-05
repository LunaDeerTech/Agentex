<script setup lang="ts">
  /**
   * ThinkingProcess Component
   *
   * Displays the agent's thinking/reasoning process with collapsible
   * step list, execution times, and real-time animations.
   */

  import { ref, computed, watch } from 'vue'
  import {
    Brain,
    ChevronDown,
    ChevronRight,
    Loader2,
    CheckCircle2,
    Clock,
    Lightbulb,
    Target,
    Search,
    Sparkles
  } from 'lucide-vue-next'

  export interface ThinkingStep {
    id: string
    name: string
    displayName?: string
    status: 'pending' | 'running' | 'completed' | 'error'
    startTime: number
    endTime?: number
    content?: string
  }

  interface Props {
    steps: ThinkingStep[]
    isActive?: boolean
    defaultExpanded?: boolean
  }

  const props = withDefaults(defineProps<Props>(), {
    isActive: false,
    defaultExpanded: true
  })

  // Expansion state
  const isExpanded = ref(props.defaultExpanded)

  // Track which steps have expanded content
  const expandedSteps = ref<Set<string>>(new Set())

  // Watch for new active steps to auto-expand
  watch(
    () => props.isActive,
    active => {
      if (active) {
        isExpanded.value = true
      }
    }
  )

  // Toggle expansion
  function toggle() {
    isExpanded.value = !isExpanded.value
  }

  // Toggle step content expansion
  function toggleStepContent(stepId: string) {
    if (expandedSteps.value.has(stepId)) {
      expandedSteps.value.delete(stepId)
    } else {
      expandedSteps.value.add(stepId)
    }
  }

  // Check if step content is expanded
  function isStepContentExpanded(stepId: string): boolean {
    return expandedSteps.value.has(stepId)
  }

  // Get step icon based on name
  function getStepIcon(stepName: string) {
    const name = stepName.toLowerCase()
    if (name.includes('think') || name.includes('reason')) return Brain
    if (name.includes('plan')) return Target
    if (name.includes('retriev') || name.includes('search')) return Search
    if (name.includes('final') || name.includes('synth')) return Sparkles
    return Lightbulb
  }

  // Get display name for step
  function getDisplayName(step: ThinkingStep): string {
    if (step.displayName) return step.displayName

    const name = step.name.toLowerCase()
    if (name === 'thinking') return '思考中'
    if (name === 'reasoning') return '推理分析'
    if (name === 'planning') return '任务规划'
    if (name === 'retrieval') return '知识检索'
    if (name === 'action') return '执行操作'
    if (name === 'synthesis') return '结果整合'
    if (name === 'final') return '生成回答'
    if (name === 'final_answer') return '最终回答'
    if (name.startsWith('executing:')) return `执行: ${name.split(':')[1]}`
    return step.name
  }

  // Format duration
  function formatDuration(step: ThinkingStep): string | null {
    if (!step.endTime) {
      // Calculate elapsed time for running steps
      if (step.status === 'running') {
        const elapsed = Date.now() - step.startTime
        if (elapsed < 1000) return `${elapsed}ms`
        return `${(elapsed / 1000).toFixed(1)}s`
      }
      return null
    }

    const duration = step.endTime - step.startTime
    if (duration < 1000) return `${duration}ms`
    return `${(duration / 1000).toFixed(1)}s`
  }

  // Summary text
  const summaryText = computed(() => {
    const running = props.steps.filter(s => s.status === 'running').length
    const completed = props.steps.filter(s => s.status === 'completed').length
    const total = props.steps.length

    if (props.isActive && running > 0) {
      return `正在执行 ${running} 个步骤...`
    }
    if (total === 0) {
      return '等待开始...'
    }
    return `${completed}/${total} 步骤完成`
  })

  // Total time
  const totalTime = computed(() => {
    if (props.steps.length === 0) return null

    const firstStart = Math.min(...props.steps.map(s => s.startTime))
    const lastEnd = props.steps
      .filter(s => s.endTime)
      .map(s => s.endTime!)
      .reduce((max, t) => Math.max(max, t), 0)

    if (lastEnd === 0) return null

    const duration = lastEnd - firstStart
    if (duration < 1000) return `${duration}ms`
    return `${(duration / 1000).toFixed(1)}s`
  })

  // Parse plan content
  function getPlanData(content: string) {
    try {
      const jsonMatch = content.match(/```(?:json)?\s*([\s\S]*?)```/)
      const jsonStr = jsonMatch ? jsonMatch[1].trim() : content.trim()
      if (!jsonStr.startsWith('{')) return null

      const data = JSON.parse(jsonStr)
      if (data.goal && Array.isArray(data.tasks)) {
        return data
      }
      return null
    } catch {
      return null
    }
  }

  // Get content preview for steps
  function getStepPreview(step: ThinkingStep): string {
    // Special preview for collapsed planning steps with valid data
    if (step.name === 'planning') {
      const data = getPlanData(step.content || '')
      if (data) {
        return `📋 已生成任务规划\n目标：${data.goal} (共 ${data.tasks.length} 个步骤)`
      }
    }
    return step.content || ''
  }
</script>

<template>
  <div
    v-if="steps.length > 0 || isActive"
    class="thinking-process border border-border/50 rounded-lg overflow-hidden bg-card/20 backdrop-blur-sm transition-all duration-300"
    :class="{ 'ring-1 ring-primary/30': isActive }"
  >
    <!-- Header -->
    <button
      class="w-full flex items-center gap-3 px-4 py-3 hover:bg-secondary/30 transition-colors text-left"
      @click="toggle"
    >
      <!-- Icon -->
      <div
        class="w-7 h-7 rounded-lg flex items-center justify-center transition-colors"
        :class="isActive ? 'bg-primary/20 text-primary' : 'bg-secondary/50 text-muted-foreground'"
      >
        <Loader2 v-if="isActive" class="w-4 h-4 animate-spin" :stroke-width="1.5" />
        <Brain v-else class="w-4 h-4" :stroke-width="1.5" />
      </div>

      <!-- Title and summary -->
      <div class="flex-1 min-w-0">
        <div class="flex items-center gap-2">
          <span class="text-sm font-medium text-foreground">思考过程</span>
          <span
            v-if="isActive"
            class="px-1.5 py-0.5 text-[10px] font-medium rounded-full bg-primary/10 text-primary animate-pulse"
          >
            进行中
          </span>
        </div>
        <p class="text-xs text-muted-foreground truncate">{{ summaryText }}</p>
      </div>

      <!-- Total time -->
      <div
        v-if="totalTime && !isActive"
        class="flex items-center gap-1 text-xs text-muted-foreground"
      >
        <Clock class="w-3 h-3" :stroke-width="1.5" />
        <span>{{ totalTime }}</span>
      </div>

      <!-- Expand icon -->
      <component
        :is="isExpanded ? ChevronDown : ChevronRight"
        class="w-4 h-4 text-muted-foreground shrink-0 transition-transform"
        :stroke-width="1.5"
      />
    </button>

    <!-- Step list -->
    <Transition
      enter-active-class="transition-all duration-300 ease-out"
      leave-active-class="transition-all duration-200 ease-in"
      enter-from-class="opacity-0 max-h-0"
      enter-to-class="opacity-100 max-h-[500px]"
      leave-from-class="opacity-100 max-h-[500px]"
      leave-to-class="opacity-0 max-h-0"
    >
      <div v-if="isExpanded" class="border-t border-border/30 overflow-hidden">
        <div class="p-3 space-y-2">
          <TransitionGroup name="step-list">
            <div
              v-for="(step, index) in steps"
              :key="step.id"
              class="step-item flex items-start gap-3 p-2 rounded-lg transition-all duration-200"
              :class="{
                'bg-primary/5': step.status === 'running',
                'hover:bg-secondary/30': step.status !== 'running'
              }"
            >
              <!-- Step number / status icon -->
              <div class="relative shrink-0">
                <!-- Connector line -->
                <div
                  v-if="index < steps.length - 1"
                  class="absolute top-7 left-1/2 -translate-x-1/2 w-px h-full bg-border/50"
                />

                <!-- Status icon -->
                <div
                  class="w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium relative z-10 transition-all duration-300"
                  :class="{
                    'bg-primary/20 text-primary animate-pulse': step.status === 'running',
                    'bg-success/20 text-success': step.status === 'completed',
                    'bg-destructive/20 text-destructive': step.status === 'error',
                    'bg-secondary text-muted-foreground': step.status === 'pending'
                  }"
                >
                  <Loader2
                    v-if="step.status === 'running'"
                    class="w-3 h-3 animate-spin"
                    :stroke-width="2"
                  />
                  <CheckCircle2
                    v-else-if="step.status === 'completed'"
                    class="w-3 h-3"
                    :stroke-width="2"
                  />
                  <component
                    :is="getStepIcon(step.name)"
                    v-else
                    class="w-3 h-3"
                    :stroke-width="2"
                  />
                </div>
              </div>

              <!-- Step content -->
              <div class="flex-1 min-w-0 pt-0.5">
                <div class="flex items-center gap-2">
                  <span
                    class="text-sm font-medium transition-colors"
                    :class="{
                      'text-primary': step.status === 'running',
                      'text-foreground': step.status === 'completed',
                      'text-muted-foreground': step.status === 'pending'
                    }"
                  >
                    {{ getDisplayName(step) }}
                  </span>

                  <!-- Duration -->
                  <span
                    v-if="formatDuration(step)"
                    class="text-[10px] font-mono text-muted-foreground/70"
                  >
                    {{ formatDuration(step) }}
                  </span>
                </div>

                <!-- Step content (clickable to expand) -->
                <div v-if="step.content" class="mt-1">
                  <!-- Custom Plan View for Planning Step -->
                  <div
                    v-if="
                      step.name === 'planning' &&
                      isStepContentExpanded(step.id) &&
                      getPlanData(step.content)
                    "
                    class="w-full text-left bg-secondary/30 rounded-lg p-3 border border-border/30 text-xs"
                  >
                    <div class="flex items-start gap-2 mb-3">
                      <span class="font-medium text-primary shrink-0 mt-0.5">目标:</span>
                      <span class="text-foreground leading-relaxed">{{
                        getPlanData(step.content).goal
                      }}</span>
                    </div>

                    <div class="space-y-2">
                      <div
                        v-for="task in getPlanData(step.content).tasks"
                        :key="task.id"
                        class="p-2.5 bg-card/50 rounded-md border border-border/50"
                      >
                        <div class="flex items-center gap-2 mb-1.5">
                          <div
                            class="font-mono text-[10px] px-1.5 py-0.5 rounded bg-primary/10 text-primary border border-primary/10"
                          >
                            {{ task.id }}
                          </div>
                          <div class="font-medium text-foreground">{{ task.title }}</div>
                        </div>
                        <div class="text-muted-foreground pl-1 mb-1.5 leading-relaxed">
                          {{ task.description }}
                        </div>

                        <div
                          v-if="task.dependencies?.length"
                          class="pl-1 flex gap-1.5 items-center flex-wrap"
                        >
                          <span class="text-[10px] text-muted-foreground/60">依赖:</span>
                          <span
                            v-for="dep in task.dependencies"
                            :key="dep"
                            class="text-[10px] px-1.5 py-0.5 rounded bg-secondary text-muted-foreground/80 border border-border/50"
                          >
                            {{ dep }}
                          </span>
                        </div>
                      </div>
                    </div>

                    <button
                      class="flex items-center gap-1 mt-3 text-[10px] text-muted-foreground/60 hover:text-foreground transition-colors"
                      @click="toggleStepContent(step.id)"
                    >
                      <component :is="ChevronDown" class="w-3 h-3" :stroke-width="1.5" />
                      <span>收起计划</span>
                    </button>
                  </div>

                  <button
                    v-else
                    class="w-full text-left group/content"
                    @click="toggleStepContent(step.id)"
                  >
                    <div
                      class="text-xs text-muted-foreground bg-secondary/30 rounded-lg p-2 hover:bg-secondary/50 transition-colors border border-border/30"
                      :class="{
                        'line-clamp-2': !isStepContentExpanded(step.id),
                        'whitespace-pre-wrap': isStepContentExpanded(step.id)
                      }"
                    >
                      {{ getStepPreview(step) }}
                    </div>
                    <div class="flex items-center gap-1 mt-1 text-[10px] text-muted-foreground/60">
                      <component
                        :is="isStepContentExpanded(step.id) ? ChevronDown : ChevronRight"
                        class="w-3 h-3"
                        :stroke-width="1.5"
                      />
                      <span>{{
                        isStepContentExpanded(step.id) ? '收起' : '展开查看思考内容'
                      }}</span>
                    </div>
                  </button>
                </div>
              </div>
            </div>
          </TransitionGroup>

          <!-- Empty state / loading -->
          <div
            v-if="steps.length === 0 && isActive"
            class="flex items-center gap-2 p-3 text-muted-foreground"
          >
            <Loader2 class="w-4 h-4 animate-spin" :stroke-width="1.5" />
            <span class="text-sm">正在初始化思考过程...</span>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
  /* Step list transitions */
  .step-list-enter-active {
    transition: all 0.3s ease-out;
  }

  .step-list-leave-active {
    transition: all 0.2s ease-in;
  }

  .step-list-enter-from {
    opacity: 0;
    transform: translateX(-10px);
  }

  .step-list-leave-to {
    opacity: 0;
    transform: translateX(10px);
  }

  .step-list-move {
    transition: transform 0.3s ease;
  }

  /* Success color for dark theme */
  .text-success {
    color: #22c55e;
  }

  .bg-success\/20 {
    background-color: rgb(34 197 94 / 0.2);
  }
</style>
