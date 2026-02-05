/**
 * Session Store
 * Manages session and message state with API integration and AG-UI streaming
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import {
  createSession as createSessionApi,
  getSessions as getSessionsApi,
  updateSession as updateSessionApi,
  deleteSession as deleteSessionApi,
  getMessages as getMessagesApi,
  createMessage as createMessageApi,
  type Session,
  type SessionCreateParams,
  type SessionUpdateParams,
  type Message
} from '@/api/session'
import { useAuthStore } from '@/stores/auth'
import {
  EventType,
  type AgentEvent,
  type RunErrorEvent,
  type TextMessageStartEvent,
  type TextMessageContentEvent,
  type TextMessageEndEvent,
  type ToolCallStartEvent,
  type ToolCallArgsEvent,
  type ToolCallEndEvent,
  type ToolCallResultEvent,
  type StepStartedEvent,
  type StepContentEvent,
  type StepFinishedEvent
} from '@/composables/agentEvents'

export interface LocalMessage extends Message {
  status?: 'pending' | 'streaming' | 'completed' | 'error'
  toolCalls?: ToolCall[]
  steps?: AgentStep[]
}

export interface ToolCall {
  id: string
  name: string
  arguments: string
  result?: string
  status: 'pending' | 'running' | 'completed' | 'error'
}

export interface AgentStep {
  name: string
  status: 'running' | 'completed'
  startTime: number
  endTime?: number
  content?: string // Thinking content for the step
}

export const useSessionStore = defineStore('session', () => {
  // ============ State ============
  const sessions = ref<Session[]>([])
  const currentSessionId = ref<string | null>(null)
  const messages = ref<Map<string, LocalMessage[]>>(new Map())
  const isStreaming = ref(false)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // AG-UI streaming state
  const abortController = ref<AbortController | null>(null)
  const currentStreamingMessageId = ref<string | null>(null)
  const currentSteps = ref<AgentStep[]>([])
  const currentToolCalls = ref<Map<string, ToolCall>>(new Map())

  // Pagination state
  const sessionPagination = ref({
    total: 0,
    page: 1,
    pageSize: 20,
    hasMore: true
  })

  // ============ Getters ============
  const currentSession = computed(
    () => sessions.value.find(s => s.id === currentSessionId.value) || null
  )

  const currentMessages = computed(() => {
    if (!currentSessionId.value) return []
    return messages.value.get(currentSessionId.value) || []
  })

  const sortedSessions = computed(() =>
    [...sessions.value].sort(
      (a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
    )
  )

  const hasMessages = computed(() => currentMessages.value.length > 0)

  // ============ Actions ============

  /**
   * Fetch sessions from API
   */
  async function fetchSessions(page = 1, append = false) {
    isLoading.value = true
    error.value = null

    try {
      const response = await getSessionsApi(page, sessionPagination.value.pageSize)

      if (append) {
        sessions.value = [...sessions.value, ...response.items]
      } else {
        sessions.value = response.items
      }

      sessionPagination.value = {
        total: response.total,
        page: response.page,
        pageSize: response.page_size,
        hasMore: response.items.length === response.page_size
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch sessions'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Create a new session
   */
  async function createSession(params: SessionCreateParams = {}) {
    isLoading.value = true
    error.value = null

    try {
      const session = await createSessionApi(params)
      sessions.value.unshift(session)
      currentSessionId.value = session.id
      messages.value.set(session.id, [])
      return session
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to create session'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Select a session and load its messages
   */
  async function selectSession(sessionId: string) {
    currentSessionId.value = sessionId

    // Load messages if not already loaded
    if (!messages.value.has(sessionId)) {
      await fetchMessages(sessionId)
    }
  }

  /**
   * Fetch messages for a session
   */
  async function fetchMessages(sessionId: string, page = 1) {
    isLoading.value = true
    error.value = null

    try {
      const response = await getMessagesApi(sessionId, page, 50)
      const existingMessages = messages.value.get(sessionId) || []

      if (page === 1) {
        messages.value.set(sessionId, response.items)
      } else {
        messages.value.set(sessionId, [...existingMessages, ...response.items])
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch messages'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Update session (e.g., rename)
   */
  async function updateSession(sessionId: string, params: SessionUpdateParams) {
    error.value = null

    try {
      const updated = await updateSessionApi(sessionId, params)
      const index = sessions.value.findIndex(s => s.id === sessionId)
      if (index !== -1) {
        sessions.value[index] = updated
      }
      return updated
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to update session'
      throw err
    }
  }

  /**
   * Delete a session
   */
  async function deleteSession(sessionId: string) {
    error.value = null

    try {
      await deleteSessionApi(sessionId)
      sessions.value = sessions.value.filter(s => s.id !== sessionId)
      messages.value.delete(sessionId)

      // If deleted session was current, clear selection
      if (currentSessionId.value === sessionId) {
        currentSessionId.value = sessions.value[0]?.id || null
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to delete session'
      throw err
    }
  }

  /**
   * Add a message locally (for optimistic updates)
   */
  function addLocalMessage(sessionId: string, message: LocalMessage) {
    const sessionMessages = messages.value.get(sessionId) || []
    sessionMessages.push(message)
    messages.value.set(sessionId, sessionMessages)

    // Update session's updated_at
    const session = sessions.value.find(s => s.id === sessionId)
    if (session) {
      session.updated_at = new Date().toISOString()
    }
  }

  /**
   * Update a message locally
   */
  function updateLocalMessage(
    sessionId: string,
    messageId: string,
    updates: Partial<LocalMessage>
  ) {
    const sessionMessages = messages.value.get(sessionId)
    if (sessionMessages) {
      const message = sessionMessages.find(m => m.id === messageId)
      if (message) {
        Object.assign(message, updates)
      }
    }
  }

  /**
   * Append content to a message (for streaming)
   */
  function appendMessageContent(sessionId: string, messageId: string, content: string) {
    const sessionMessages = messages.value.get(sessionId)
    if (sessionMessages) {
      const message = sessionMessages.find(m => m.id === messageId)
      if (message) {
        message.content += content
      }
    }
  }

  /**
   * Handle AG-UI SSE event
   */
  function handleAgentEvent(event: AgentEvent, sessionId: string, assistantMessageId: string) {
    switch (event.type) {
      case EventType.RUN_ERROR:
        handleRunError(event as RunErrorEvent, sessionId, assistantMessageId)
        break
      case EventType.TEXT_MESSAGE_START:
        handleTextStart(event as TextMessageStartEvent, sessionId, assistantMessageId)
        break
      case EventType.TEXT_MESSAGE_CONTENT:
        handleTextContent(event as TextMessageContentEvent, sessionId, assistantMessageId)
        break
      case EventType.TEXT_MESSAGE_END:
        handleTextEnd(event as TextMessageEndEvent, sessionId, assistantMessageId)
        break
      case EventType.TOOL_CALL_START:
        handleToolStart(event as ToolCallStartEvent)
        break
      case EventType.TOOL_CALL_ARGS:
        handleToolArgs(event as ToolCallArgsEvent)
        break
      case EventType.TOOL_CALL_END:
        handleToolEnd(event as ToolCallEndEvent)
        break
      case EventType.TOOL_CALL_RESULT:
        handleToolResult(event as ToolCallResultEvent, sessionId, assistantMessageId)
        break
      case EventType.STEP_STARTED:
        handleStepStarted(event as StepStartedEvent, sessionId, assistantMessageId)
        break
      case EventType.STEP_CONTENT:
        handleStepContent(event as StepContentEvent, sessionId, assistantMessageId)
        break
      case EventType.STEP_FINISHED:
        handleStepFinished(event as StepFinishedEvent, sessionId, assistantMessageId)
        break
    }
  }

  function handleRunError(event: RunErrorEvent, sessionId: string, messageId: string) {
    error.value = event.message
    updateLocalMessage(sessionId, messageId, {
      content: `Error: ${event.message}`,
      status: 'error'
    })
    isStreaming.value = false
  }

  function handleTextStart(event: TextMessageStartEvent, sessionId: string, messageId: string) {
    currentStreamingMessageId.value = event.message_id
    // Update message id if we have a new one from the server
    if (event.message_id !== messageId) {
      updateLocalMessage(sessionId, messageId, { id: event.message_id })
    }
  }

  function handleTextContent(event: TextMessageContentEvent, sessionId: string, messageId: string) {
    const targetId = currentStreamingMessageId.value || messageId
    appendMessageContent(sessionId, targetId, event.delta)
  }

  function handleTextEnd(_event: TextMessageEndEvent, sessionId: string, messageId: string) {
    const targetId = currentStreamingMessageId.value || messageId
    updateLocalMessage(sessionId, targetId, { status: 'completed' })
    currentStreamingMessageId.value = null
    // Copy accumulated tool calls and steps to the message
    const sessionMessages = messages.value.get(sessionId)
    if (sessionMessages) {
      const message = sessionMessages.find(m => m.id === targetId)
      if (message) {
        message.toolCalls = Array.from(currentToolCalls.value.values())
        message.steps = [...currentSteps.value]
      }
    }
  }

  function handleToolStart(event: ToolCallStartEvent) {
    currentToolCalls.value.set(event.tool_call_id, {
      id: event.tool_call_id,
      name: event.tool_call_name,
      arguments: '',
      status: 'running'
    })
  }

  function handleToolArgs(event: ToolCallArgsEvent) {
    const call = currentToolCalls.value.get(event.tool_call_id)
    if (call) {
      call.arguments += event.delta
    }
  }

  function handleToolEnd(event: ToolCallEndEvent) {
    const call = currentToolCalls.value.get(event.tool_call_id)
    if (call) {
      call.status = 'pending'
    }
  }

  function handleToolResult(event: ToolCallResultEvent, _sessionId: string, _messageId: string) {
    const call = currentToolCalls.value.get(event.tool_call_id)
    if (call) {
      call.result = event.content
      call.status = 'completed'
    }
  }

  function handleStepStarted(event: StepStartedEvent, sessionId: string, messageId: string) {
    console.log('[Session] Step started:', event.step_name)
    const newStep: AgentStep = {
      name: event.step_name,
      status: 'running',
      startTime: event.timestamp,
      content: '' // Initialize with empty content
    }
    currentSteps.value.push(newStep)
    // Also update the streaming message's steps for real-time display
    const sessionMessages = messages.value.get(sessionId)
    const streamingMsgId = currentStreamingMessageId.value || messageId
    const streamingMessage = sessionMessages?.find(
      m => m.id === streamingMsgId || m.id === messageId
    )
    if (streamingMessage) {
      if (!streamingMessage.steps) streamingMessage.steps = []
      streamingMessage.steps.push({ ...newStep })
    }
    console.log('[Session] Current steps:', currentSteps.value)
  }

  function handleStepContent(event: StepContentEvent, sessionId: string, messageId: string) {
    console.log(
      '[Session] Step content received:',
      event.step_name,
      'delta length:',
      event.delta.length
    )
    // Find the running step and append content
    const step = currentSteps.value.find(s => s.name === event.step_name && s.status === 'running')
    if (step) {
      step.content = (step.content || '') + event.delta
      console.log('[Session] Step content updated, total length:', step.content.length)
    } else {
      console.warn(
        '[Session] No running step found for:',
        event.step_name,
        'Current steps:',
        currentSteps.value
      )
    }
    // Also update the streaming message's steps for real-time display
    const sessionMessages = messages.value.get(sessionId)
    const streamingMsgId = currentStreamingMessageId.value || messageId
    const streamingMessage = sessionMessages?.find(
      m => m.id === streamingMsgId || m.id === messageId
    )
    if (streamingMessage && streamingMessage.steps) {
      const msgStep = streamingMessage.steps.find(
        s => s.name === event.step_name && s.status === 'running'
      )
      if (msgStep) {
        msgStep.content = (msgStep.content || '') + event.delta
      }
    }
  }

  function handleStepFinished(event: StepFinishedEvent, sessionId: string, messageId: string) {
    console.log('[Session] Step finished:', event.step_name)
    const step = currentSteps.value.find(s => s.name === event.step_name && s.status === 'running')
    if (step) {
      step.status = 'completed'
      step.endTime = event.timestamp
      console.log('[Session] Step content length:', step.content?.length || 0)
    }
    // Also update the streaming message's steps for real-time display
    const sessionMessages = messages.value.get(sessionId)
    const streamingMsgId = currentStreamingMessageId.value || messageId
    const streamingMessage = sessionMessages?.find(
      m => m.id === streamingMsgId || m.id === messageId
    )
    if (streamingMessage && streamingMessage.steps) {
      const msgStep = streamingMessage.steps.find(
        s => s.name === event.step_name && s.status === 'running'
      )
      if (msgStep) {
        msgStep.status = 'completed'
        msgStep.endTime = event.timestamp
      }
    }
  }

  /**
   * Send a user message with AG-UI streaming
   */
  async function sendMessage(content: string) {
    if (!currentSessionId.value || !content.trim()) return

    const authStore = useAuthStore()
    const sessionId = currentSessionId.value
    const session = sessions.value.find(s => s.id === sessionId)

    // Reset streaming state
    currentToolCalls.value.clear()
    currentSteps.value = []
    currentStreamingMessageId.value = null

    // Create optimistic user message
    const tempId = `temp-${Date.now()}`
    const userMessage: LocalMessage = {
      id: tempId,
      session_id: sessionId,
      role: 'user',
      content: content.trim(),
      meta: {},
      created_at: new Date().toISOString(),
      status: 'pending'
    }

    addLocalMessage(sessionId, userMessage)
    isStreaming.value = true
    error.value = null

    try {
      // Send user message to API for persistence
      const savedMessage = await createMessageApi(sessionId, {
        role: 'user',
        content: content.trim()
      })

      // Update with real ID
      updateLocalMessage(sessionId, tempId, {
        id: savedMessage.id,
        status: 'completed'
      })

      // Create placeholder for assistant response
      const assistantMessageId = `assistant-${Date.now()}`
      const assistantMessage: LocalMessage = {
        id: assistantMessageId,
        session_id: sessionId,
        role: 'assistant',
        content: '',
        meta: {},
        created_at: new Date().toISOString(),
        status: 'streaming',
        toolCalls: [],
        steps: []
      }

      addLocalMessage(sessionId, assistantMessage)

      // Build message history for AG-UI
      const sessionMessages = messages.value.get(sessionId) || []
      const messageHistory = sessionMessages
        .filter(m => m.status === 'completed' && m.id !== assistantMessageId)
        .map(m => ({
          id: m.id,
          role: m.role,
          content: m.content
        }))

      // Prepare AG-UI request
      const baseUrl = import.meta.env.VITE_API_URL || '/api/v1'
      const runInput = {
        thread_id: sessionId,
        run_id: `run-${Date.now()}`,
        messages: messageHistory,
        tools: [],
        state: {},
        forwarded_props: {
          agent_type: session?.agent_type || 'react',
          model_id: session?.model_config_id || null,
          temperature: 0.7,
          max_tokens: 4096,
          system_prompt: null
        }
      }

      // Create abort controller
      abortController.value = new AbortController()

      // Call AG-UI streaming endpoint
      const response = await fetch(`${baseUrl}/agent/run`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${authStore.token}`,
          Accept: 'text/event-stream'
        },
        body: JSON.stringify(runInput),
        signal: abortController.value.signal
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      if (!response.body) {
        throw new Error('Response body is null')
      }

      // Read SSE stream
      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()

        if (done) {
          break
        }

        buffer += decoder.decode(value, { stream: true })

        // Process complete events from buffer
        const lines = buffer.split('\n')
        buffer = lines.pop() || '' // Keep incomplete line in buffer

        let currentEventType = ''
        let currentEventData = ''

        for (const line of lines) {
          if (line.startsWith('event: ')) {
            currentEventType = line.slice(7).trim()
          } else if (line.startsWith('data: ')) {
            currentEventData = line.slice(6)
          } else if (line === '' && currentEventType && currentEventData) {
            // Empty line signals end of event
            try {
              const event = JSON.parse(currentEventData) as AgentEvent
              handleAgentEvent(event, sessionId, assistantMessageId)
            } catch (e) {
              console.error('Failed to parse AG-UI event:', e)
            }
            currentEventType = ''
            currentEventData = ''
          }
        }
      }

      // Mark as completed if still streaming
      const currentAssistantMessage = messages.value
        .get(sessionId)
        ?.find(m => m.id === assistantMessageId || m.id === currentStreamingMessageId.value)
      if (currentAssistantMessage && currentAssistantMessage.status === 'streaming') {
        currentAssistantMessage.status = 'completed'
        currentAssistantMessage.toolCalls = Array.from(currentToolCalls.value.values())
        currentAssistantMessage.steps = [...currentSteps.value]
      }
    } catch (err) {
      if ((err as Error).name === 'AbortError') {
        // User cancelled - mark message as completed with current content
        const sessionMessages = messages.value.get(sessionId)
        const lastMessage = sessionMessages?.[sessionMessages.length - 1]
        if (lastMessage?.status === 'streaming') {
          lastMessage.status = 'completed'
          if (!lastMessage.content) {
            lastMessage.content = '[Generation stopped by user]'
          }
        }
      } else {
        updateLocalMessage(sessionId, tempId, { status: 'error' })
        error.value = err instanceof Error ? err.message : 'Failed to send message'
        // Update assistant message with error
        const sessionMessages = messages.value.get(sessionId)
        const lastMessage = sessionMessages?.[sessionMessages.length - 1]
        if (lastMessage?.role === 'assistant' && lastMessage.status === 'streaming') {
          lastMessage.status = 'error'
          lastMessage.content = error.value || 'An error occurred'
        }
        throw err
      }
    } finally {
      isStreaming.value = false
      abortController.value = null
    }
  }

  /**
   * Set streaming state
   */
  function setStreaming(streaming: boolean) {
    isStreaming.value = streaming
  }

  /**
   * Stop current streaming request
   */
  function stopStreaming() {
    // Abort the fetch request
    if (abortController.value) {
      abortController.value.abort()
      abortController.value = null
    }

    isStreaming.value = false

    // Mark the last assistant message as completed if it was streaming
    if (currentSessionId.value) {
      const sessionMessages = messages.value.get(currentSessionId.value)
      if (sessionMessages) {
        const lastMessage = sessionMessages[sessionMessages.length - 1]
        if (lastMessage?.status === 'streaming') {
          lastMessage.status = 'completed'
          if (!lastMessage.content) {
            lastMessage.content = '[Generation stopped by user]'
          }
          // Attach accumulated tool calls and steps
          lastMessage.toolCalls = Array.from(currentToolCalls.value.values())
          lastMessage.steps = [...currentSteps.value]
        }
      }
    }
  }

  /**
   * Regenerate the last assistant message
   */
  async function regenerateLastMessage() {
    if (!currentSessionId.value) return

    const authStore = useAuthStore()
    const sessionId = currentSessionId.value
    const session = sessions.value.find(s => s.id === sessionId)
    const sessionMessages = messages.value.get(sessionId)

    if (!sessionMessages || sessionMessages.length < 2) return

    // Find the last user message
    let lastUserMessage: LocalMessage | undefined
    for (let i = sessionMessages.length - 1; i >= 0; i--) {
      const msg = sessionMessages[i]
      if (msg && msg.role === 'user') {
        lastUserMessage = msg
        break
      }
    }

    if (!lastUserMessage) return

    // Remove the last assistant message
    const lastMessage = sessionMessages[sessionMessages.length - 1]
    if (lastMessage?.role === 'assistant') {
      sessionMessages.pop()
    }

    // Reset streaming state
    currentToolCalls.value.clear()
    currentSteps.value = []
    currentStreamingMessageId.value = null
    isStreaming.value = true
    error.value = null

    try {
      // Create new placeholder for assistant response
      const assistantMessageId = `assistant-${Date.now()}`
      const assistantMessage: LocalMessage = {
        id: assistantMessageId,
        session_id: sessionId,
        role: 'assistant',
        content: '',
        meta: {},
        created_at: new Date().toISOString(),
        status: 'streaming',
        toolCalls: [],
        steps: []
      }

      addLocalMessage(sessionId, assistantMessage)

      // Build message history for AG-UI (excluding the message we just added)
      const messageHistory = sessionMessages
        .filter(m => m.status === 'completed')
        .map(m => ({
          id: m.id,
          role: m.role,
          content: m.content
        }))

      // Prepare AG-UI request
      const baseUrl = import.meta.env.VITE_API_URL || '/api/v1'
      const runInput = {
        thread_id: sessionId,
        run_id: `run-${Date.now()}`,
        messages: messageHistory,
        tools: [],
        state: {},
        forwarded_props: {
          agent_type: session?.agent_type || 'react',
          model_id: session?.model_config_id || null,
          temperature: 0.7,
          max_tokens: 4096,
          system_prompt: null
        }
      }

      // Create abort controller
      abortController.value = new AbortController()

      // Call AG-UI streaming endpoint
      const response = await fetch(`${baseUrl}/agent/run`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${authStore.token}`,
          Accept: 'text/event-stream'
        },
        body: JSON.stringify(runInput),
        signal: abortController.value.signal
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      if (!response.body) {
        throw new Error('Response body is null')
      }

      // Read SSE stream
      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()

        if (done) {
          break
        }

        buffer += decoder.decode(value, { stream: true })

        // Process complete events from buffer
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        let currentEventType = ''
        let currentEventData = ''

        for (const line of lines) {
          if (line.startsWith('event: ')) {
            currentEventType = line.slice(7).trim()
          } else if (line.startsWith('data: ')) {
            currentEventData = line.slice(6)
          } else if (line === '' && currentEventType && currentEventData) {
            try {
              const event = JSON.parse(currentEventData) as AgentEvent
              handleAgentEvent(event, sessionId, assistantMessageId)
            } catch (e) {
              console.error('Failed to parse AG-UI event:', e)
            }
            currentEventType = ''
            currentEventData = ''
          }
        }
      }

      // Mark as completed if still streaming
      const currentAssistantMessage = messages.value
        .get(sessionId)
        ?.find(m => m.id === assistantMessageId || m.id === currentStreamingMessageId.value)
      if (currentAssistantMessage && currentAssistantMessage.status === 'streaming') {
        currentAssistantMessage.status = 'completed'
        currentAssistantMessage.toolCalls = Array.from(currentToolCalls.value.values())
        currentAssistantMessage.steps = [...currentSteps.value]
      }
    } catch (err) {
      if ((err as Error).name === 'AbortError') {
        const currentMessages = messages.value.get(sessionId)
        const lastMsg = currentMessages?.[currentMessages.length - 1]
        if (lastMsg?.status === 'streaming') {
          lastMsg.status = 'completed'
          if (!lastMsg.content) {
            lastMsg.content = '[Generation stopped by user]'
          }
        }
      } else {
        error.value = err instanceof Error ? err.message : 'Failed to regenerate'
        const currentMessages = messages.value.get(sessionId)
        const lastMsg = currentMessages?.[currentMessages.length - 1]
        if (lastMsg?.role === 'assistant' && lastMsg.status === 'streaming') {
          lastMsg.status = 'error'
          lastMsg.content = error.value || 'An error occurred'
        }
        throw err
      }
    } finally {
      isStreaming.value = false
      abortController.value = null
    }
  }

  /**
   * Clear all sessions
   */
  function clearSessions() {
    sessions.value = []
    messages.value.clear()
    currentSessionId.value = null
  }

  return {
    // State
    sessions,
    currentSessionId,
    messages,
    isStreaming,
    isLoading,
    error,
    sessionPagination,
    currentSteps,
    currentToolCalls,

    // Getters
    currentSession,
    currentMessages,
    sortedSessions,
    hasMessages,

    // Actions
    fetchSessions,
    createSession,
    selectSession,
    fetchMessages,
    updateSession,
    deleteSession,
    addLocalMessage,
    updateLocalMessage,
    appendMessageContent,
    sendMessage,
    setStreaming,
    stopStreaming,
    regenerateLastMessage,
    clearSessions
  }
})
