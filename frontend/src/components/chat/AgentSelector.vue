<script setup lang="ts">
  /**
   * AgentSelector Component
   *
   * Dropdown selector for choosing agent types with descriptions
   * and visual indicators.
   */

  import { ref, computed, watch } from 'vue'
  import {
    Bot,
    Brain,
    BookOpen,
    ListTodo,
    ChevronDown,
    Check,
    Info,
    Sparkles
  } from 'lucide-vue-next'

  interface AgentType {
    id: string
    name: string
    description: string
    icon?: string
    capabilities: string[]
  }

  // Agent type definitions
  const AGENT_TYPES: AgentType[] = [
    {
      id: 'react',
      name: 'ReAct Agent',
      description: '通用对话 Agent，支持多轮推理和工具调用',
      icon: 'brain',
      capabilities: ['多轮推理', '工具调用', '灵活对话']
    },
    {
      id: 'agentic_rag',
      name: 'RAG Agent',
      description: '知识增强 Agent，可检索知识库进行精准回答',
      icon: 'book-open',
      capabilities: ['知识检索', '来源引用', '精准问答']
    },
    {
      id: 'plan_execute',
      name: 'Plan & Execute',
      description: '任务规划 Agent，将复杂任务分解为步骤执行',
      icon: 'list-todo',
      capabilities: ['任务分解', '依赖管理', '进度追踪']
    }
  ]

  interface Props {
    modelValue?: string | null
    disabled?: boolean
    showLabel?: boolean
  }

  const props = withDefaults(defineProps<Props>(), {
    modelValue: 'react',
    disabled: false,
    showLabel: false
  })

  const emit = defineEmits<{
    'update:modelValue': [value: string]
  }>()

  // Dropdown state
  const isOpen = ref(false)
  const dropdownRef = ref<HTMLElement | null>(null)

  // Selected agent
  const selectedAgent = computed(() => {
    return AGENT_TYPES.find(a => a.id === props.modelValue) || AGENT_TYPES[0]
  })

  // Get icon component
  function getIconComponent(iconName: string | undefined) {
    switch (iconName) {
      case 'brain':
        return Brain
      case 'book-open':
        return BookOpen
      case 'list-todo':
        return ListTodo
      default:
        return Bot
    }
  }

  // Toggle dropdown
  function toggleDropdown() {
    if (props.disabled) return
    isOpen.value = !isOpen.value
  }

  // Select agent
  function selectAgent(agentId: string) {
    emit('update:modelValue', agentId)
    isOpen.value = false
  }

  // Close on outside click
  function handleClickOutside(event: MouseEvent) {
    if (dropdownRef.value && !dropdownRef.value.contains(event.target as Node)) {
      isOpen.value = false
    }
  }

  // Add/remove click listener
  watch(isOpen, open => {
    if (open) {
      document.addEventListener('click', handleClickOutside)
    } else {
      document.removeEventListener('click', handleClickOutside)
    }
  })
</script>

<template>
  <div ref="dropdownRef" class="agent-selector relative">
    <!-- Label -->
    <label v-if="showLabel" class="block text-xs font-medium text-muted-foreground mb-1.5">
      Agent 类型
    </label>

    <!-- Trigger button -->
    <button
      type="button"
      class="flex items-center gap-2 px-2 py-1.5 rounded-lg transition-colors outline-none"
      :class="[
        disabled
          ? 'cursor-not-allowed opacity-50 text-muted-foreground'
          : isOpen
            ? 'bg-accent text-foreground'
            : 'text-muted-foreground hover:bg-accent hover:text-foreground'
      ]"
      :disabled="disabled"
      @click="toggleDropdown"
      title="Select agent type"
    >
      <!-- Agent icon -->
      <component
        :is="getIconComponent(selectedAgent.icon)"
        class="w-4 h-4"
        :class="{ 'text-primary': !disabled }"
        :stroke-width="1.5"
      />

      <!-- Agent name -->
      <span class="text-xs font-medium text-left truncate">
        {{ selectedAgent.name }}
      </span>

      <!-- Chevron -->
      <ChevronDown
        class="w-3 h-3 opacity-50 transition-transform"
        :class="{ 'rotate-180': isOpen }"
        :stroke-width="1.5"
      />
    </button>

    <!-- Dropdown menu -->
    <Transition
      enter-active-class="transition duration-200 ease-out"
      leave-active-class="transition duration-150 ease-in"
      enter-from-class="opacity-0 scale-95 translate-y-1"
      enter-to-class="opacity-100 scale-100 translate-y-0"
      leave-from-class="opacity-100 scale-100 translate-y-0"
      leave-to-class="opacity-0 scale-95 translate-y-1"
    >
      <div
        v-if="isOpen"
        class="absolute z-50 mb-2 bottom-full left-0 w-80 rounded-xl border border-border/50 bg-card shadow-lg shadow-black/20 overflow-hidden origin-bottom-left"
      >
        <!-- Header -->
        <div class="px-3 py-2 border-b border-border/30 bg-secondary/30">
          <div class="flex items-center gap-2 text-xs text-muted-foreground">
            <Sparkles class="w-3 h-3" :stroke-width="1.5" />
            <span>选择 Agent 架构</span>
          </div>
        </div>

        <!-- Options -->
        <div class="p-1.5 max-h-[300px] overflow-y-auto">
          <button
            v-for="agent in AGENT_TYPES"
            :key="agent.id"
            type="button"
            class="w-full flex items-start gap-3 p-3 rounded-lg text-left transition-colors"
            :class="[
              agent.id === modelValue
                ? 'bg-primary/10 border border-primary/20'
                : 'hover:bg-secondary/50 border border-transparent'
            ]"
            @click="selectAgent(agent.id)"
          >
            <!-- Icon -->
            <div
              class="w-9 h-9 rounded-lg flex items-center justify-center shrink-0"
              :class="[
                agent.id === modelValue
                  ? 'bg-primary/20 text-primary'
                  : 'bg-secondary text-muted-foreground'
              ]"
            >
              <component :is="getIconComponent(agent.icon)" class="w-4 h-4" :stroke-width="1.5" />
            </div>

            <!-- Content -->
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2">
                <span
                  class="text-sm font-medium"
                  :class="[agent.id === modelValue ? 'text-primary' : 'text-foreground']"
                >
                  {{ agent.name }}
                </span>
                <Check
                  v-if="agent.id === modelValue"
                  class="w-4 h-4 text-primary"
                  :stroke-width="2"
                />
              </div>
              <p class="text-xs text-muted-foreground mt-0.5 line-clamp-2">
                {{ agent.description }}
              </p>

              <!-- Capabilities -->
              <div class="flex flex-wrap gap-1 mt-2">
                <span
                  v-for="cap in agent.capabilities"
                  :key="cap"
                  class="px-1.5 py-0.5 text-[10px] rounded-full bg-secondary text-muted-foreground"
                >
                  {{ cap }}
                </span>
              </div>
            </div>
          </button>
        </div>

        <!-- Footer hint -->
        <div class="px-3 py-2 border-t border-border/30 bg-secondary/20 flex items-center gap-2">
          <Info class="w-3 h-3 text-muted-foreground/70" :stroke-width="1.5" />
          <span class="text-[10px] text-muted-foreground/70"> 不同 Agent 架构适用于不同场景 </span>
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
  /* Scrollbar styling for dropdown */
  .max-h-\[300px\]::-webkit-scrollbar {
    width: 4px;
  }

  .max-h-\[300px\]::-webkit-scrollbar-track {
    background: transparent;
  }

  .max-h-\[300px\]::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 2px;
  }

  .max-h-\[300px\]::-webkit-scrollbar-thumb:hover {
    background: rgba(255, 255, 255, 0.2);
  }
</style>
