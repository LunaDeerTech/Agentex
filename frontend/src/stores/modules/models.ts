import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import {
  listModels,
  createModel,
  updateModel,
  deleteModel,
  testModel,
  setDefaultModel,
  type LLMModel,
  type LLMModelCreateRequest,
  type LLMModelUpdateRequest,
  type LLMModelTestResponse
} from '@/api/models'

export const useModelsStore = defineStore('models', () => {
  // State
  const models = ref<LLMModel[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const testingModelId = ref<string | null>(null)

  // Getters
  const defaultModel = computed(() => models.value.find(m => m.is_default))

  const enabledModels = computed(() => models.value.filter(m => m.is_enabled))

  const modelsByProvider = computed(() => {
    const grouped: Record<string, LLMModel[]> = {}
    for (const model of models.value) {
      const provider = model.provider
      if (!grouped[provider]) {
        grouped[provider] = []
      }
      grouped[provider]!.push(model)
    }
    return grouped
  })

  // Actions
  async function fetchModels() {
    isLoading.value = true
    error.value = null
    try {
      const response = await listModels()
      // Response is unwrapped by axios interceptor
      models.value = (response as any).models || []
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch models'
      throw e
    } finally {
      isLoading.value = false
    }
  }

  async function addModel(data: LLMModelCreateRequest): Promise<LLMModel> {
    isLoading.value = true
    error.value = null
    try {
      const model = (await createModel(data)) as unknown as LLMModel
      models.value.unshift(model)
      // If this is the new default, update other models
      if (model.is_default) {
        models.value.forEach(m => {
          if (m.id !== model.id) {
            m.is_default = false
          }
        })
      }
      return model
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to create model'
      throw e
    } finally {
      isLoading.value = false
    }
  }

  async function editModel(modelId: string, data: LLMModelUpdateRequest): Promise<LLMModel> {
    isLoading.value = true
    error.value = null
    try {
      const updatedModel = (await updateModel(modelId, data)) as unknown as LLMModel
      const index = models.value.findIndex(m => m.id === modelId)
      if (index !== -1) {
        models.value[index] = updatedModel
      }
      // If this is the new default, update other models
      if (updatedModel.is_default) {
        models.value.forEach(m => {
          if (m.id !== modelId) {
            m.is_default = false
          }
        })
      }
      return updatedModel
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to update model'
      throw e
    } finally {
      isLoading.value = false
    }
  }

  async function removeModel(modelId: string): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      await deleteModel(modelId)
      models.value = models.value.filter(m => m.id !== modelId)
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to delete model'
      throw e
    } finally {
      isLoading.value = false
    }
  }

  async function testModelConnection(modelId: string): Promise<LLMModelTestResponse> {
    testingModelId.value = modelId
    error.value = null
    try {
      const result = (await testModel(modelId)) as unknown as LLMModelTestResponse
      return result
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to test model'
      throw e
    } finally {
      testingModelId.value = null
    }
  }

  async function makeDefault(modelId: string): Promise<LLMModel> {
    isLoading.value = true
    error.value = null
    try {
      const updatedModel = (await setDefaultModel(modelId)) as unknown as LLMModel
      // Update local state
      models.value.forEach(m => {
        m.is_default = m.id === modelId
      })
      return updatedModel
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to set default model'
      throw e
    } finally {
      isLoading.value = false
    }
  }

  function getModelById(modelId: string): LLMModel | undefined {
    return models.value.find(m => m.id === modelId)
  }

  function $reset() {
    models.value = []
    isLoading.value = false
    error.value = null
    testingModelId.value = null
  }

  return {
    // State
    models,
    isLoading,
    error,
    testingModelId,
    // Getters
    defaultModel,
    enabledModels,
    modelsByProvider,
    // Actions
    fetchModels,
    addModel,
    editModel,
    removeModel,
    testModelConnection,
    makeDefault,
    getModelById,
    $reset
  }
})
