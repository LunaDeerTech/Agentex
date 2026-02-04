<template>
  <div class="relative" ref="containerRef">
    <button
      type="button"
      @click="toggleDropdown"
      class="flex items-center gap-2 px-3 py-2 rounded-lg border border-[var(--color-border-default)] bg-[var(--color-bg-surface)] text-[var(--color-text-primary)] hover:bg-[var(--color-bg-muted)] transition-colors w-full"
      :class="{ 'ring-2 ring-[var(--color-primary)]': isOpen }"
    >
      <template v-if="selectedModel">
        <span class="text-lg">{{ getProviderIcon(selectedModel.provider) }}</span>
        <span class="flex-1 text-left truncate">{{ selectedModel.name }}</span>
        <span class="text-xs text-[var(--color-text-tertiary)]">
          {{ selectedModel.model_id }}
        </span>
      </template>
      <template v-else>
        <span class="text-[var(--color-text-tertiary)]">Select a model</span>
      </template>
      <svg
        class="w-4 h-4 text-[var(--color-text-tertiary)] transition-transform"
        :class="{ 'rotate-180': isOpen }"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
      </svg>
    </button>

    <!-- Dropdown -->
    <Transition
      enter-active-class="transition duration-100 ease-out"
      enter-from-class="transform scale-95 opacity-0"
      enter-to-class="transform scale-100 opacity-100"
      leave-active-class="transition duration-75 ease-in"
      leave-from-class="transform scale-100 opacity-100"
      leave-to-class="transform scale-95 opacity-0"
    >
      <div
        v-if="isOpen"
        class="absolute z-50 mt-1 w-full bg-[var(--color-bg-surface)] border border-[var(--color-border-default)] rounded-lg shadow-lg overflow-hidden"
      >
        <!-- Loading -->
        <div v-if="isLoading" class="p-4 text-center text-[var(--color-text-tertiary)]">
          Loading models...
        </div>

        <!-- Empty -->
        <div v-else-if="enabledModels.length === 0" class="p-4 text-center">
          <p class="text-[var(--color-text-tertiary)] text-sm mb-2">No models configured</p>
          <button @click="goToSettings" class="text-sm text-[var(--color-primary)] hover:underline">
            Add a model →
          </button>
        </div>

        <!-- Models List -->
        <div v-else class="max-h-64 overflow-y-auto">
          <div
            v-for="provider in Object.keys(modelsByProvider)"
            :key="provider"
            class="border-b border-[var(--color-border-muted)] last:border-b-0"
          >
            <!-- Provider Header -->
            <div
              class="px-3 py-2 bg-[var(--color-bg-muted)] text-xs font-medium text-[var(--color-text-tertiary)] uppercase tracking-wide"
            >
              {{ getProviderLabel(provider) }}
            </div>

            <!-- Provider Models -->
            <button
              v-for="model in modelsByProvider[provider]"
              :key="model.id"
              type="button"
              @click="selectModel(model)"
              class="w-full flex items-center gap-3 px-3 py-2 hover:bg-[var(--color-bg-muted)] transition-colors"
              :class="{
                'bg-[var(--color-bg-muted)]': modelValue === model.id
              }"
            >
              <span class="text-lg">{{ getProviderIcon(model.provider) }}</span>
              <div class="flex-1 text-left">
                <div class="flex items-center gap-2">
                  <span class="text-[var(--color-text-primary)]">{{ model.name }}</span>
                  <span
                    v-if="model.is_default"
                    class="px-1.5 py-0.5 text-xs rounded bg-[var(--color-primary)]/10 text-[var(--color-primary)]"
                  >
                    Default
                  </span>
                </div>
                <div class="text-xs text-[var(--color-text-tertiary)]">
                  {{ model.model_id }}
                </div>
              </div>
              <svg
                v-if="modelValue === model.id"
                class="w-4 h-4 text-[var(--color-primary)]"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fill-rule="evenodd"
                  d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                  clip-rule="evenodd"
                />
              </svg>
            </button>
          </div>
        </div>

        <!-- Footer -->
        <div class="border-t border-[var(--color-border-muted)] p-2">
          <button
            @click="goToSettings"
            class="w-full text-left px-3 py-2 text-sm text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] hover:bg-[var(--color-bg-muted)] rounded transition-colors"
          >
            ⚙️ Manage models
          </button>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
  import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
  import { useRouter } from 'vue-router'
  import { storeToRefs } from 'pinia'
  import { useModelsStore } from '@/stores/modules/models'
  import { getProviderLabel, getProviderIcon, type LLMModel } from '@/api/models'

  const props = defineProps<{
    modelValue?: string | null
  }>()

  const emit = defineEmits<{
    'update:modelValue': [value: string | null]
    change: [model: LLMModel | null]
  }>()

  const router = useRouter()
  const store = useModelsStore()
  const { models, isLoading, enabledModels, modelsByProvider, defaultModel } = storeToRefs(store)

  const isOpen = ref(false)
  const containerRef = ref<HTMLElement | null>(null)

  // Selected model
  const selectedModel = computed(() => {
    if (!props.modelValue) return defaultModel.value
    return models.value.find(m => m.id === props.modelValue) || defaultModel.value
  })

  // Methods
  const toggleDropdown = () => {
    isOpen.value = !isOpen.value
  }

  const selectModel = (model: LLMModel) => {
    emit('update:modelValue', model.id)
    emit('change', model)
    isOpen.value = false
  }

  const goToSettings = () => {
    router.push('/settings/models')
    isOpen.value = false
  }

  // Close on click outside
  const handleClickOutside = (event: MouseEvent) => {
    if (containerRef.value && !containerRef.value.contains(event.target as Node)) {
      isOpen.value = false
    }
  }

  // Auto-select default model if none selected
  watch(
    [enabledModels, () => props.modelValue],
    ([models, value]) => {
      if (!value && models.length > 0) {
        const defaultM = models.find(m => m.is_default) || models[0]
        if (defaultM) {
          emit('update:modelValue', defaultM.id)
          emit('change', defaultM)
        }
      }
    },
    { immediate: true }
  )

  onMounted(() => {
    document.addEventListener('click', handleClickOutside)
    if (models.value.length === 0) {
      store.fetchModels()
    }
  })

  onUnmounted(() => {
    document.removeEventListener('click', handleClickOutside)
  })
</script>
