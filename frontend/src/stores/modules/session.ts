import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface Message {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  createdAt: string
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

export interface Session {
  id: string
  title: string
  modelId: string
  messages: Message[]
  createdAt: string
  updatedAt: string
}

export const useSessionStore = defineStore('session', () => {
  // State
  const sessions = ref<Session[]>([])
  const currentSessionId = ref<string | null>(null)
  const isStreaming = ref(false)

  // Getters
  const currentSession = computed(
    () => sessions.value.find(s => s.id === currentSessionId.value) || null
  )

  const currentMessages = computed(() => currentSession.value?.messages || [])

  const sortedSessions = computed(() =>
    [...sessions.value].sort(
      (a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()
    )
  )

  // Actions
  function setCurrentSession(sessionId: string | null) {
    currentSessionId.value = sessionId
  }

  function addSession(session: Session) {
    sessions.value.push(session)
    currentSessionId.value = session.id
  }

  function addMessage(sessionId: string, message: Message) {
    const session = sessions.value.find(s => s.id === sessionId)
    if (session) {
      session.messages.push(message)
      session.updatedAt = new Date().toISOString()
    }
  }

  function updateMessage(sessionId: string, messageId: string, updates: Partial<Message>) {
    const session = sessions.value.find(s => s.id === sessionId)
    if (session) {
      const message = session.messages.find(m => m.id === messageId)
      if (message) {
        Object.assign(message, updates)
      }
    }
  }

  function setStreaming(streaming: boolean) {
    isStreaming.value = streaming
  }

  function clearSessions() {
    sessions.value = []
    currentSessionId.value = null
  }

  return {
    // State
    sessions,
    currentSessionId,
    isStreaming,
    // Getters
    currentSession,
    currentMessages,
    sortedSessions,
    // Actions
    setCurrentSession,
    addSession,
    addMessage,
    updateMessage,
    setStreaming,
    clearSessions
  }
})
