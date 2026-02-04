<template>
  <div class="space-y-8 animate-in fade-in duration-500">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h3 class="text-2xl font-semibold tracking-tight text-foreground">LLM Models</h3>
        <p class="text-sm text-muted-foreground mt-1">
          Configure your AI model providers and API credentials.
        </p>
      </div>
      <Button :disabled="isLoading" class="shrink-0 gap-2" @click="openCreateDialog">
        <Plus class="w-4 h-4" />
        Add Model
      </Button>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading && models.length === 0" class="flex justify-center py-20">
      <Loader2 class="w-8 h-8 animate-spin text-muted-foreground" />
    </div>

    <!-- Empty State -->
    <div
      v-else-if="models.length === 0"
      class="flex flex-col items-center justify-center p-16 text-center border border-dashed border-border rounded-lg bg-muted/20"
    >
      <div class="flex items-center justify-center w-16 h-16 rounded-full bg-muted mb-6">
        <Bot class="w-8 h-8 text-muted-foreground" />
      </div>
      <h3 class="text-lg font-medium text-foreground mb-2">No models configured</h3>
      <p class="text-sm text-muted-foreground max-w-sm mb-8 leading-relaxed">
        Add your first LLM model to start using AI features. We support OpenAI and Anthropic
        providers.
      </p>
      <Button class="gap-2" @click="openCreateDialog">
        <Plus class="w-4 h-4" />
        Add Your First Model
      </Button>
    </div>

    <!-- Models List -->
    <div v-else class="grid gap-4">
      <TransitionGroup name="list" appear>
        <Card
          v-for="model in models"
          :key="model.id"
          class="p-5 group transition-all duration-200 hover:border-primary/20"
        >
          <div class="flex flex-col sm:flex-row sm:items-start justify-between gap-5">
            <div class="flex items-start gap-4">
              <!-- Provider Icon -->
              <div
                class="w-12 h-12 rounded-xl bg-muted flex items-center justify-center text-2xl shrink-0"
              >
                {{ getProviderIcon(model.provider) }}
              </div>

              <!-- Model Info -->
              <div class="space-y-1">
                <div class="flex items-center gap-2 flex-wrap">
                  <span class="font-medium text-foreground text-lg">
                    {{ model.name }}
                  </span>
                  <div class="flex items-center gap-2">
                    <span
                      v-if="model.is_default"
                      class="px-2 py-0.5 text-xs font-medium rounded-full bg-primary/10 text-primary border border-primary/20"
                    >
                      Default
                    </span>
                    <span
                      v-if="!model.is_enabled"
                      class="px-2 py-0.5 text-xs font-medium rounded-full bg-muted text-muted-foreground"
                    >
                      Disabled
                    </span>
                  </div>
                </div>

                <div class="text-sm text-muted-foreground flex items-center gap-2">
                  <span class="capitalize">{{ getProviderLabel(model.provider) }}</span>
                  <span class="text-border">•</span>
                  <span class="font-mono text-xs bg-muted px-1.5 py-0.5 rounded">{{
                    model.model_id
                  }}</span>
                </div>

                <div
                  class="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-muted-foreground mt-2"
                >
                  <div class="flex items-center gap-1.5" title="API Key">
                    <Key class="w-3.5 h-3.5" />
                    <span class="font-mono">{{ model.api_key_masked }}</span>
                  </div>
                  <div
                    v-if="model.base_url"
                    class="flex items-center gap-1.5"
                    title="Custom Base URL"
                  >
                    <Globe class="w-3.5 h-3.5" />
                    <span class="truncate max-w-50">{{ model.base_url }}</span>
                  </div>
                  <div class="flex items-center gap-1.5" title="Temperature">
                    <Thermometer class="w-3.5 h-3.5" />
                    <span>{{ model.temperature }}</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Actions -->
            <div class="flex items-center gap-1 self-start sm:self-center">
              <Button
                variant="ghost"
                size="sm"
                class="h-9 px-3 text-muted-foreground hover:text-foreground"
                :disabled="testingModelId === model.id"
                @click="handleTest(model)"
              >
                <Loader2 v-if="testingModelId === model.id" class="w-4 h-4 mr-2 animate-spin" />
                <Play v-else class="w-4 h-4 mr-2" />
                Test
              </Button>
              <Button
                v-if="!model.is_default && model.is_enabled"
                variant="ghost"
                size="sm"
                class="h-9 px-3 text-muted-foreground hover:text-foreground"
                :disabled="isLoading"
                @click="handleSetDefault(model)"
              >
                Default
              </Button>
              <Button
                variant="ghost"
                size="icon"
                class="h-9 w-9 text-muted-foreground hover:text-foreground"
                @click="openEditDialog(model)"
              >
                <Edit2 class="w-4 h-4" />
              </Button>
              <Button
                variant="ghost"
                size="icon"
                class="h-9 w-9 text-muted-foreground hover:text-destructive hover:bg-destructive/10"
                :disabled="isLoading"
                @click="handleDelete(model)"
              >
                <Trash2 class="w-4 h-4" />
              </Button>
            </div>
          </div>

          <!-- Test Result -->
          <div
            v-if="testResults[model.id]"
            class="mt-4 p-3 rounded-md text-sm border flex items-start gap-3 animate-in fade-in slide-in-from-top-1"
            :class="
              testResults[model.id]?.success
                ? 'bg-green-500/10 border-green-500/20 text-green-500'
                : 'bg-destructive/10 border-destructive/20 text-destructive'
            "
          >
            <CheckCircle2 v-if="testResults[model.id]?.success" class="w-5 h-5 shrink-0" />
            <XCircle v-else class="w-5 h-5 shrink-0" />
            <div class="flex-1">
              <div class="font-medium">
                {{ testResults[model.id]?.success ? 'Connection Successful' : 'Connection Failed' }}
              </div>
              <div class="text-sm opacity-90 mt-0.5">{{ testResults[model.id]?.message }}</div>
              <div
                v-if="testResults[model.id]?.latency_ms"
                class="text-xs mt-1.5 opacity-70 font-mono"
              >
                Latency: {{ testResults[model.id]?.latency_ms }}ms
              </div>
            </div>
          </div>
        </Card>
      </TransitionGroup>
    </div>

    <!-- Create/Edit Dialog Overlay -->
    <div
      v-if="showDialog"
      class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200"
      @click.self="closeDialog"
    >
      <div
        class="bg-popover border border-border rounded-xl shadow-2xl w-full max-w-lg max-h-[90vh] overflow-hidden flex flex-col animate-in zoom-in-95 duration-200"
      >
        <div
          class="p-6 border-b border-border flex flex-row items-center justify-between sticky top-0 bg-popover z-10"
        >
          <h4 class="text-lg font-semibold text-foreground">
            {{ isEditing ? 'Edit Model' : 'Add Model' }}
          </h4>
          <Button variant="ghost" size="icon" class="h-8 w-8 rounded-full" @click="closeDialog">
            <X class="w-4 h-4" />
          </Button>
        </div>

        <form class="p-6 space-y-5 overflow-y-auto" @submit.prevent="handleSubmit">
          <!-- Name -->
          <div class="space-y-1.5">
            <label class="block text-sm font-medium text-foreground"> Name </label>
            <Input v-model="formData.name" placeholder="e.g. My GPT-4 Model" required />
          </div>

          <!-- Provider -->
          <div class="space-y-1.5">
            <label class="block text-sm font-medium text-foreground"> Provider </label>
            <div class="relative">
              <select
                v-model="formData.provider"
                class="w-full h-10 px-3 rounded-md border border-input bg-muted/50 text-foreground focus:outline-none focus:ring-1 focus:ring-ring focus:border-ring transition-colors disabled:opacity-50 appearance-none"
                :disabled="isEditing"
                required
              >
                <option v-for="p in PROVIDER_OPTIONS" :key="p.value" :value="p.value">
                  {{ p.label }}
                </option>
              </select>
              <!-- Custom Arrow for Select -->
              <div class="absolute right-3 top-2.5 pointer-events-none text-muted-foreground">
                <ChevronsUpDown class="w-4 h-4" />
              </div>
            </div>
          </div>

          <!-- Model ID -->
          <div class="space-y-1.5">
            <label class="block text-sm font-medium text-foreground"> Model </label>
            <div class="relative">
              <select
                v-model="formData.model_id"
                class="w-full h-10 px-3 rounded-md border border-input bg-muted/50 text-foreground focus:outline-none focus:ring-1 focus:ring-ring focus:border-ring transition-colors disabled:opacity-50 appearance-none"
                required
              >
                <option value="" disabled>Select a model</option>
                <option v-for="m in currentModelPresets" :key="m.value" :value="m.value">
                  {{ m.label }}
                </option>
                <option value="custom">Custom Model ID</option>
              </select>
              <div class="absolute right-3 top-2.5 pointer-events-none text-muted-foreground">
                <ChevronsUpDown class="w-4 h-4" />
              </div>
            </div>

            <div v-if="formData.model_id === 'custom'" class="mt-2 animate-in slide-in-from-top-1">
              <Input
                v-model="customModelId"
                placeholder="Enter custom model ID (e.g. gpt-4-0125-preview)"
                required
              />
            </div>
          </div>

          <!-- API Key -->
          <div class="space-y-1.5">
            <label class="block text-sm font-medium text-foreground">
              API Key
              <span v-if="isEditing" class="font-normal text-muted-foreground ml-1">
                (leave blank to keep existing)
              </span>
            </label>
            <Input
              v-model="formData.api_key"
              type="password"
              :placeholder="isEditing ? '••••••••' : 'sk-...'"
              :required="!isEditing"
            />
          </div>

          <!-- Base URL (Advanced) -->
          <div class="space-y-1.5">
            <div class="flex items-center justify-between">
              <label class="block text-sm font-medium text-foreground"> Custom Base URL </label>
              <span class="text-xs text-muted-foreground">Optional</span>
            </div>
            <Input v-model="formData.base_url" placeholder="https://api.openai.com/v1" />
            <p class="text-[0.8rem] text-muted-foreground">
              For Azure OpenAI, local deployments, or proxy servers.
            </p>
          </div>

          <!-- Parameters Grid -->
          <div class="grid grid-cols-3 gap-4 p-4 rounded-lg bg-muted/30 border border-border">
            <div class="space-y-1.5">
              <label class="text-xs font-medium text-muted-foreground uppercase tracking-wider">
                Max Tokens
              </label>
              <Input
                v-model="formData.max_tokens"
                type="number"
                min="1"
                max="200000"
                class="h-8 text-xs bg-background"
              />
            </div>
            <div class="space-y-1.5">
              <label class="text-xs font-medium text-muted-foreground uppercase tracking-wider">
                Temperature
              </label>
              <Input
                v-model="formData.temperature"
                type="number"
                min="0"
                max="2"
                step="0.1"
                class="h-8 text-xs bg-background"
              />
            </div>
            <div class="space-y-1.5">
              <label class="text-xs font-medium text-muted-foreground uppercase tracking-wider">
                Top P
              </label>
              <Input
                v-model="formData.top_p"
                type="number"
                min="0"
                max="1"
                step="0.1"
                class="h-8 text-xs bg-background"
              />
            </div>
          </div>

          <!-- Toggles -->
          <div class="space-y-4 pt-2">
            <label
              class="flex items-center justify-between cursor-pointer p-3 rounded-lg border border-border bg-muted/20 hover:bg-muted/40 transition-colors"
            >
              <span class="text-sm font-medium text-foreground">Set as default model</span>
              <input
                v-model="formData.is_default"
                type="checkbox"
                class="w-4 h-4 rounded border-input text-primary focus:ring-primary bg-background"
              />
            </label>
            <label
              v-if="isEditing"
              class="flex items-center justify-between cursor-pointer p-3 rounded-lg border border-border bg-muted/20 hover:bg-muted/40 transition-colors"
            >
              <span class="text-sm font-medium text-foreground">Enable model</span>
              <input
                v-model="formData.is_enabled"
                type="checkbox"
                class="w-4 h-4 rounded border-input text-primary focus:ring-primary bg-background"
              />
            </label>
          </div>

          <!-- Description -->
          <div class="space-y-1.5">
            <label class="block text-sm font-medium text-foreground"> Description </label>
            <Input v-model="formData.description" placeholder="Optional notes about this model" />
          </div>

          <!-- Error Message -->
          <div
            v-if="formError"
            class="p-3 rounded-md bg-destructive/10 text-destructive text-sm flex items-start gap-2"
          >
            <AlertCircle class="w-4 h-4 shrink-0 mt-0.5" />
            {{ formError }}
          </div>

          <!-- Footer -->
          <div class="flex justify-end gap-3 pt-4 border-t border-border">
            <Button type="button" variant="ghost" @click="closeDialog"> Cancel </Button>
            <Button type="submit" :disabled="isSubmitting" class="min-w-25">
              <Loader2 v-if="isSubmitting" class="w-4 h-4 mr-2 animate-spin" />
              {{ isSubmitting ? 'Saving...' : isEditing ? 'Save Changes' : 'Create Model' }}
            </Button>
          </div>
        </form>
      </div>
    </div>

    <!-- Delete Confirmation Dialog -->
    <div
      v-if="showDeleteConfirm"
      class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200"
      @click.self="showDeleteConfirm = false"
    >
      <div
        class="bg-popover border border-border rounded-xl shadow-2xl w-full max-w-md p-6 animate-in zoom-in-95 duration-200"
      >
        <div class="flex items-center gap-4 mb-4">
          <div
            class="w-10 h-10 rounded-full bg-destructive/10 flex items-center justify-center shrink-0"
          >
            <AlertTriangle class="w-5 h-5 text-destructive" />
          </div>
          <div>
            <h4 class="text-lg font-semibold text-foreground">Delete Model</h4>
            <p class="text-sm text-muted-foreground mt-1">
              Are you sure you want to delete this model?
            </p>
          </div>
        </div>

        <div class="p-3 rounded-lg bg-muted border border-border mb-6">
          <span class="font-medium text-foreground">{{ modelToDelete?.name }}</span>
          <div class="text-xs text-muted-foreground mt-1 font-mono">
            {{ modelToDelete?.model_id }}
          </div>
        </div>

        <div class="flex justify-end gap-3">
          <Button variant="ghost" @click="showDeleteConfirm = false"> Cancel </Button>
          <Button variant="destructive" :disabled="isLoading" @click="confirmDelete">
            Delete Model
          </Button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { ref, computed, onMounted, reactive, watch } from 'vue'
  import { useModelsStore } from '@/stores/modules/models'
  import {
    PROVIDER_OPTIONS,
    MODEL_PRESETS,
    getProviderLabel,
    getProviderIcon,
    type LLMModel,
    type LLMProvider,
    type LLMModelTestResponse
  } from '@/api/models'

  // Components
  import Button from '@/components/ui/Button.vue'
  import Input from '@/components/ui/Input.vue'
  import Card from '@/components/ui/Card.vue'

  // Icons
  import {
    Bot,
    Plus,
    Loader2,
    Trash2,
    Edit2,
    Play,
    CheckCircle2,
    XCircle,
    Key,
    Globe,
    Thermometer,
    X,
    AlertCircle,
    AlertTriangle,
    ChevronsUpDown
  } from 'lucide-vue-next'

  import { storeToRefs } from 'pinia'

  const store = useModelsStore()
  const { models, isLoading, testingModelId } = storeToRefs(store)

  // Dialog state
  const showDialog = ref(false)
  const isEditing = ref(false)
  const editingModelId = ref<string | null>(null)
  const isSubmitting = ref(false)
  const formError = ref<string | null>(null)
  const customModelId = ref('')

  // Delete confirmation
  const showDeleteConfirm = ref(false)
  const modelToDelete = ref<LLMModel | null>(null)

  // Test results
  const testResults = reactive<Record<string, LLMModelTestResponse>>({})

  // Form data
  const defaultFormData = () => ({
    name: '',
    provider: 'openai' as LLMProvider,
    model_id: '',
    api_key: '',
    base_url: '',
    max_tokens: 4096,
    temperature: 0.7,
    top_p: 1.0,
    is_default: false,
    is_enabled: true,
    description: ''
  })

  const formData = reactive(defaultFormData())

  // Computed
  const currentModelPresets = computed(() => {
    return MODEL_PRESETS[formData.provider as LLMProvider] || []
  })

  // Watch provider changes to reset model_id
  watch(
    () => formData.provider,
    () => {
      formData.model_id = ''
      customModelId.value = ''
    }
  )

  // Methods
  const openCreateDialog = () => {
    Object.assign(formData, defaultFormData())
    customModelId.value = ''
    isEditing.value = false
    editingModelId.value = null
    formError.value = null
    showDialog.value = true
  }

  const openEditDialog = (model: LLMModel) => {
    Object.assign(formData, {
      name: model.name,
      provider: model.provider as LLMProvider,
      model_id: model.model_id,
      api_key: '',
      base_url: model.base_url || '',
      max_tokens: model.max_tokens,
      temperature: model.temperature,
      top_p: model.top_p,
      is_default: model.is_default,
      is_enabled: model.is_enabled,
      description: model.description || ''
    })

    // Check if model_id is a preset or custom
    const presets = MODEL_PRESETS[model.provider as LLMProvider] || []
    if (!presets.find(p => p.value === model.model_id)) {
      customModelId.value = model.model_id
      formData.model_id = 'custom'
    }

    isEditing.value = true
    editingModelId.value = model.id
    formError.value = null
    showDialog.value = true
  }

  const closeDialog = () => {
    showDialog.value = false
  }

  const handleSubmit = async () => {
    formError.value = null
    isSubmitting.value = true

    try {
      const modelId = formData.model_id === 'custom' ? customModelId.value : formData.model_id

      if (isEditing.value && editingModelId.value) {
        // Build update payload
        const updateData: Record<string, any> = {}
        if (formData.name) updateData.name = formData.name
        if (modelId) updateData.model_id = modelId
        if (formData.api_key) updateData.api_key = formData.api_key
        updateData.base_url = formData.base_url || null
        updateData.max_tokens = formData.max_tokens
        updateData.temperature = formData.temperature
        updateData.top_p = formData.top_p
        updateData.is_default = formData.is_default
        updateData.is_enabled = formData.is_enabled
        updateData.description = formData.description || null

        await store.editModel(editingModelId.value, updateData)
      } else {
        // Create new model
        await store.addModel({
          name: formData.name,
          provider: formData.provider,
          model_id: modelId,
          api_key: formData.api_key,
          base_url: formData.base_url || undefined,
          max_tokens: formData.max_tokens,
          temperature: formData.temperature,
          top_p: formData.top_p,
          is_default: formData.is_default,
          description: formData.description || undefined
        })
      }

      closeDialog()
    } catch (e) {
      formError.value = e instanceof Error ? e.message : 'An error occurred'
    } finally {
      isSubmitting.value = false
    }
  }

  const handleTest = async (model: LLMModel) => {
    try {
      const result = await store.testModelConnection(model.id)
      testResults[model.id] = result
    } catch (e) {
      testResults[model.id] = {
        success: false,
        message: e instanceof Error ? e.message : 'Test failed',
        response_text: null,
        latency_ms: null,
        model_info: null
      }
    }
  }

  const handleSetDefault = async (model: LLMModel) => {
    try {
      await store.makeDefault(model.id)
    } catch (e) {
      console.error('Failed to set default:', e)
    }
  }

  const handleDelete = (model: LLMModel) => {
    modelToDelete.value = model
    showDeleteConfirm.value = true
  }

  const confirmDelete = async () => {
    if (!modelToDelete.value) return

    try {
      await store.removeModel(modelToDelete.value.id)
      showDeleteConfirm.value = false
      modelToDelete.value = null
    } catch (e) {
      console.error('Failed to delete:', e)
    }
  }

  // Lifecycle
  onMounted(() => {
    store.fetchModels()
  })
</script>

<style scoped>
  .list-move, /* apply transition to moving elements */
.list-enter-active,
.list-leave-active {
    transition: all 0.3s ease;
  }

  .list-enter-from,
  .list-leave-to {
    opacity: 0;
    transform: translateY(10px);
  }

  /* Ensure leave items are taken out of layout flow so others move smoothly */
  .list-leave-active {
    position: absolute;
    width: 100%;
  }
</style>
