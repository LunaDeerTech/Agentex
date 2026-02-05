<template>
  <div ref="containerRef" class="relative">
    <button
      type="button"
      class="flex items-center gap-1.5 px-2 py-1.5 rounded-lg text-muted-foreground hover:text-foreground hover:bg-white/5 transition-colors text-xs max-w-[200px]"
      :class="{ 'text-foreground bg-white/5': isOpen }"
      title="Select model"
      @click="toggleDropdown"
    >
      <template v-if="selectedModel">
        <span class="text-base flex-shrink-0">{{ getProviderIcon(selectedModel.provider) }}</span>
        <span class="flex-1 text-left truncate font-medium">{{ selectedModel.name }}</span>
      </template>
      <template v-else>
        <span class="text-muted-foreground">Select a model</span>
      </template>
      <svg
        class="w-3 h-3 text-muted-foreground/50 transition-transform flex-shrink-0"
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
        class="absolute z-50 mb-2 bottom-full right-0 w-64 bg-background border border-border rounded-xl shadow-xl overflow-hidden"
      >
        <!-- Loading -->
        <div v-if="isLoading" class="p-4 text-center text-muted-foreground">Loading models...</div>

        <!-- Empty -->
        <div v-else-if="enabledModels.length === 0" class="p-4 text-center">
          <p class="text-muted-foreground text-sm mb-2">No models configured</p>
          <button class="text-sm text-primary hover:underline" @click="goToSettings">
            Add a model →
          </button>
        </div>

        <!-- Models List -->
        <div v-else class="max-h-64 overflow-y-auto">
          <div
            v-for="provider in Object.keys(modelsByProvider)"
            :key="provider"
            class="border-b border-border/50 last:border-b-0"
          >
            <!-- Provider Header -->
            <div
              class="px-3 py-2 bg-muted/50 text-xs font-medium text-muted-foreground uppercase tracking-wide"
            >
              {{ getProviderLabel(provider) }}
            </div>

            <!-- Provider Models -->
            <button
              v-for="model in modelsByProvider[provider]"
              :key="model.id"
              type="button"
              class="w-full flex items-center gap-3 px-3 py-2 hover:bg-muted/50 transition-colors"
              :class="{
                'bg-muted': modelValue === model.id
              }"
              @click="selectModel(model)"
            >
              <span class="text-lg">{{ getProviderIcon(model.provider) }}</span>
              <div class="flex-1 text-left">
                <div class="flex items-center gap-2">
                  <span class="text-foreground text-sm">{{ model.name }}</span>
                  <span
                    v-if="model.is_default"
                    class="px-1.5 py-0.5 text-[10px] rounded bg-primary/10 text-primary uppercase font-bold"
                  >
                    Default
                  </span>
                </div>
                <div class="text-[10px] text-muted-foreground">
                  {{ model.model_id }}
                </div>
              </div>
              <svg
                v-if="modelValue === model.id"
                class="w-4 h-4 text-primary"
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
        <div class="border-t border-border p-2 bg-muted/20">
          <button
            class="w-full text-left px-3 py-2 text-xs text-muted-foreground hover:text-foreground hover:bg-muted rounded transition-colors flex items-center gap-2"
            @click="goToSettings"
          >
            <span>⚙️</span> Manage models
          </button>
        </div>
      </div>
    </Transition>
  </div>
</template>
>

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
