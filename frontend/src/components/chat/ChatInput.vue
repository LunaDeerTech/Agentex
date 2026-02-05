<script setup lang="ts">
  /**
   * ChatInput Component
   * The input area for composing and sending messages
   */

  import { ref, computed, watch, nextTick } from 'vue'
  import { storeToRefs } from 'pinia'
  import { Send, Paperclip, Square } from 'lucide-vue-next'
  import { useSessionStore } from '@/stores/session'
  import { useModelsStore } from '@/stores/modules/models'
  import ModelSelector from './ModelSelector.vue'

  const sessionStore = useSessionStore()
  const modelsStore = useModelsStore()
  const { defaultModel } = storeToRefs(modelsStore)

  const inputMessage = ref('')
  const textareaRef = ref<HTMLTextAreaElement | null>(null)
  const isFocused = ref(false)
  const selectedModelId = ref<string | null>(null)

  // Initialize selectedModelId
  watch(
    () => sessionStore.currentSession,
    session => {
      if (session?.model_config_id) {
        selectedModelId.value = session.model_config_id
      } else if (!selectedModelId.value && defaultModel.value) {
        selectedModelId.value = defaultModel.value.id
      }
    },
    { immediate: true }
  )

  // Also watch default model
  watch(defaultModel, model => {
    if (!selectedModelId.value && !sessionStore.currentSession && model) {
      selectedModelId.value = model.id
    }
  })

  // Handle model change
  async function handleModelChange(modelId: string | null) {
    selectedModelId.value = modelId

    // If we have an active session, update it
    if (sessionStore.currentSession && modelId) {
      try {
        await sessionStore.updateSession(sessionStore.currentSession.id, {
          model_config_id: modelId
        })
      } catch (err) {
        console.error('Failed to update session model:', err)
      }
    }
  }

  // Computed states
  const canSend = computed(() => inputMessage.value.trim().length > 0 && !sessionStore.isStreaming)
  const isStreaming = computed(() => sessionStore.isStreaming)
  const hasSession = computed(() => sessionStore.currentSession !== null)

  // Auto-resize textarea
  function autoResize() {
    nextTick(() => {
      if (textareaRef.value) {
        textareaRef.value.style.height = 'auto'
        const newHeight = Math.min(textareaRef.value.scrollHeight, 200)
        textareaRef.value.style.height = `${newHeight}px`
      }
    })
  }

  watch(inputMessage, autoResize)

  // Send message
  async function handleSend() {
    if (!canSend.value) return

    const content = inputMessage.value.trim()
    inputMessage.value = ''

    // Reset textarea height
    if (textareaRef.value) {
      textareaRef.value.style.height = 'auto'
    }

    // Create session if none exists
    if (!hasSession.value) {
      try {
        await sessionStore.createSession({
          title: content.slice(0, 50) + (content.length > 50 ? '...' : ''),
          agent_type: 'react',
          model_config_id: selectedModelId.value || undefined
        })
      } catch (err) {
        console.error('Failed to create session:', err)
        inputMessage.value = content // Restore input on error
        return
      }
    }

    // Send the message
    try {
      await sessionStore.sendMessage(content)
    } catch (err) {
      console.error('Failed to send message:', err)
    }
  }

  // Stop streaming
  function handleStop() {
    sessionStore.setStreaming(false)
    // TODO: Actually cancel the streaming request
  }

  // Handle keyboard shortcuts
  function handleKeydown(e: KeyboardEvent) {
    // Enter to send (without Shift)
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  // Focus input
  function focusInput() {
    textareaRef.value?.focus()
  }

  // Expose focus method
  defineExpose({ focusInput })
</script>

<template>
  <div class="p-4 md:p-6 lg:p-8 max-w-4xl mx-auto w-full">
    <div
      class="relative flex flex-col bg-secondary/40 backdrop-blur-sm border rounded-xl transition-all shadow-lg"
      :class="[
        isFocused
          ? 'border-primary/50 ring-1 ring-primary/20'
          : 'border-border/50 hover:border-border/80'
      ]"
    >
      <!-- Textarea -->
      <textarea
        ref="textareaRef"
        v-model="inputMessage"
        class="w-full bg-transparent border-none text-sm p-4 min-h-[60px] max-h-[200px] resize-none focus:ring-0 focus:outline-none placeholder:text-muted-foreground/70 font-sans leading-relaxed"
        placeholder="Type your message..."
        rows="1"
        :disabled="isStreaming"
        @keydown="handleKeydown"
        @focus="isFocused = true"
        @blur="isFocused = false"
      />

      <!-- Bottom toolbar -->
      <div class="flex items-center justify-between p-2 pl-4 border-t border-border/30">
        <!-- Left side: attachments -->
        <div class="flex items-center gap-2">
          <!-- Attach button -->
          <button
            class="p-2 text-muted-foreground hover:text-foreground hover:bg-white/5 rounded-lg transition-colors"
            title="Attach file"
            :disabled="isStreaming"
          >
            <Paperclip class="w-4 h-4" :stroke-width="1.5" />
          </button>
        </div>

        <!-- Right side: model selector and send/stop button -->
        <div class="flex items-center gap-2">
          <!-- Model selector -->
          <ModelSelector
            :model-value="selectedModelId"
            @update:model-value="handleModelChange"
            class="hidden md:block"
          />

          <!-- Stop button (when streaming) -->
          <button
            v-if="isStreaming"
            class="flex items-center gap-2 px-3 py-2 bg-destructive/10 text-destructive border border-destructive/20 rounded-lg hover:bg-destructive/20 transition-colors"
            @click="handleStop"
          >
            <Square class="w-4 h-4" fill="currentColor" :stroke-width="0" />
            <span class="text-sm font-medium">Stop</span>
          </button>

          <!-- Send button -->
          <button
            v-else
            class="p-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-sm hover:shadow-md hover:shadow-primary/20"
            :disabled="!canSend"
            title="Send message (Enter)"
            @click="handleSend"
          >
            <Send class="w-4 h-4" :stroke-width="1.5" />
          </button>
        </div>
      </div>
    </div>

    <!-- Disclaimer -->
    <div class="text-center mt-3 text-[10px] text-muted-foreground/60 font-mono">
      Agentex can make mistakes. Consider checking important information.
    </div>
  </div>
</template>
