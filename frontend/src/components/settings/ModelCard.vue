<script setup lang="ts">
  import { type PropType } from 'vue'
  import {
    Key,
    Globe,
    Thermometer,
    Loader2,
    Play,
    Edit2,
    Trash2,
    CheckCircle2,
    XCircle
  } from 'lucide-vue-next'
  import { getProviderIcon, getProviderLabel } from '@/api/models'
  import type { LLMModel, LLMModelTestResponse } from '@/api/models'
  import Button from '@/components/ui/Button.vue'
  import Card from '@/components/ui/Card.vue'

  const props = defineProps({
    model: {
      type: Object as PropType<LLMModel>,
      required: true
    },
    isLoading: Boolean,
    testingModelId: String as PropType<string | null>,
    testResult: Object as PropType<LLMModelTestResponse | undefined>
  })

  const emit = defineEmits<{
    (e: 'test', model: LLMModel): void
    (e: 'set-default', model: LLMModel): void
    (e: 'edit', model: LLMModel): void
    (e: 'delete', model: LLMModel): void
  }>()
</script>

<template>
  <Card class="p-5 group transition-all duration-200 hover:border-primary/20">
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
            <div v-if="model.base_url" class="flex items-center gap-1.5" title="Custom Base URL">
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
          @click="$emit('test', model)"
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
          @click="$emit('set-default', model)"
        >
          Default
        </Button>
        <Button
          variant="ghost"
          size="icon"
          class="h-9 w-9 text-muted-foreground hover:text-foreground"
          @click="$emit('edit', model)"
        >
          <Edit2 class="w-4 h-4" />
        </Button>
        <Button
          variant="ghost"
          size="icon"
          class="h-9 w-9 text-muted-foreground hover:text-destructive hover:bg-destructive/10"
          :disabled="isLoading"
          @click="$emit('delete', model)"
        >
          <Trash2 class="w-4 h-4" />
        </Button>
      </div>
    </div>

    <!-- Test Result -->
    <div
      v-if="testResult"
      class="mt-4 p-3 rounded-md text-sm border flex items-start gap-3 animate-in fade-in slide-in-from-top-1"
      :class="
        testResult.success
          ? 'bg-green-500/10 border-green-500/20 text-green-500'
          : 'bg-destructive/10 border-destructive/20 text-destructive'
      "
    >
      <CheckCircle2 v-if="testResult.success" class="w-5 h-5 shrink-0" />
      <XCircle v-else class="w-5 h-5 shrink-0" />
      <div class="flex-1">
        <div class="font-medium">
          {{ testResult.success ? 'Connection Successful' : 'Connection Failed' }}
        </div>
        <div class="text-sm opacity-90 mt-0.5">{{ testResult.message }}</div>
        <div v-if="testResult.latency_ms" class="text-xs mt-1.5 opacity-70 font-mono">
          Latency: {{ testResult.latency_ms }}ms
        </div>
      </div>
    </div>
  </Card>
</template>
