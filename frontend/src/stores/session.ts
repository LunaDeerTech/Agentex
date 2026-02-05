/**
 * Session Store
 * Manages session and message state with API integration
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

export interface LocalMessage extends Message {
  status?: 'pending' | 'streaming' | 'completed' | 'error'
  toolCalls?: ToolCall[]
}

export interface ToolCall {
  id: string
  name: string
  arguments: Record<string, unknown>
  result?: unknown
  status: 'pending' | 'running' | 'completed' | 'error'
}

export const useSessionStore = defineStore('session', () => {
  // ============ State ============
  const sessions = ref<Session[]>([])
  const currentSessionId = ref<string | null>(null)
  const messages = ref<Map<string, LocalMessage[]>>(new Map())
  const isStreaming = ref(false)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

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
   * Send a user message
   */
  async function sendMessage(content: string) {
    if (!currentSessionId.value || !content.trim()) return

    const sessionId = currentSessionId.value

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

    try {
      // Send to API
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
      const assistantMessage: LocalMessage = {
        id: `temp-assistant-${Date.now()}`,
        session_id: sessionId,
        role: 'assistant',
        content: '',
        meta: {},
        created_at: new Date().toISOString(),
        status: 'streaming'
      }

      addLocalMessage(sessionId, assistantMessage)

      // TODO: Integrate with AG-UI streaming endpoint
      // For now, simulate a response
      setTimeout(() => {
        updateLocalMessage(sessionId, assistantMessage.id, {
          content:
            'This is a placeholder response. AG-UI streaming will be implemented in the next phase.',
          status: 'completed'
        })
        isStreaming.value = false
      }, 1000)
    } catch (err) {
      updateLocalMessage(sessionId, tempId, { status: 'error' })
      isStreaming.value = false
      error.value = err instanceof Error ? err.message : 'Failed to send message'
      throw err
    }
  }

  /**
   * Set streaming state
   */
  function setStreaming(streaming: boolean) {
    isStreaming.value = streaming
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
    clearSessions
  }
})
