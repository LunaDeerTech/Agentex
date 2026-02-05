/**
 * useAgentChat Composable
 *
 * Provides reactive state and methods for agent chat interactions
 * using the AG-UI (Agent-User Interaction Protocol) over SSE.
 */

import { ref, reactive, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import {
  EventType,
  type AgentEvent,
  type RunStartedEvent,
  type RunFinishedEvent,
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
} from './agentEvents'

// Types
export interface Message {
  id: string
  role: 'user' | 'assistant' | 'system' | 'tool'
  content: string
  status?: 'pending' | 'streaming' | 'completed' | 'error'
  toolCalls?: ToolCall[]
  createdAt: Date
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
  content?: string // Store step content (e.g., thinking process)
}

export interface Tool {
  name: string
  description: string
  parameters: Record<string, unknown>
}

export interface RunAgentInput {
  thread_id: string
  run_id?: string
  messages: Array<{
    id: string
    role: string
    content: string
  }>
  tools?: Tool[]
  forwarded_props?: {
    agent_type?: string
    model_id?: string
    temperature?: number
    max_tokens?: number
    system_prompt?: string
  }
}

export interface UseAgentChatOptions {
  onRunStart?: (event: RunStartedEvent) => void
  onRunFinish?: (event: RunFinishedEvent) => void
  onRunError?: (event: RunErrorEvent) => void
  onTextStart?: (event: TextMessageStartEvent) => void
  onTextContent?: (event: TextMessageContentEvent) => void
  onTextEnd?: (event: TextMessageEndEvent) => void
  onToolStart?: (event: ToolCallStartEvent) => void
  onToolArgs?: (event: ToolCallArgsEvent) => void
  onToolEnd?: (event: ToolCallEndEvent) => void
  onToolResult?: (event: ToolCallResultEvent) => void
  onStepStart?: (event: StepStartedEvent) => void
  onStepContent?: (event: StepContentEvent) => void
  onStepFinish?: (event: StepFinishedEvent) => void
}

export function useAgentChat(options: UseAgentChatOptions = {}) {
  const authStore = useAuthStore()

  // State
  const isRunning = ref(false)
  const isStreaming = ref(false)
  const currentRunId = ref<string | null>(null)
  const error = ref<string | null>(null)
  const currentStep = ref<string | null>(null)
  const steps = reactive<AgentStep[]>([])
  const currentMessageId = ref<string | null>(null)
  const currentMessage = ref<string>('')
  const toolCalls = reactive<Map<string, ToolCall>>(new Map())
  const abortController = ref<AbortController | null>(null)

  // Track message content by ID
  const messageContents = reactive<Map<string, string>>(new Map())

  // Computed
  const canAbort = computed(() => isRunning.value && abortController.value !== null)

  /**
   * Process incoming SSE event
   */
  function handleEvent(event: AgentEvent) {
    switch (event.type) {
      case EventType.RUN_STARTED:
        handleRunStarted(event as RunStartedEvent)
        break
      case EventType.RUN_FINISHED:
        handleRunFinished(event as RunFinishedEvent)
        break
      case EventType.RUN_ERROR:
        handleRunError(event as RunErrorEvent)
        break
      case EventType.TEXT_MESSAGE_START:
        handleTextStart(event as TextMessageStartEvent)
        break
      case EventType.TEXT_MESSAGE_CONTENT:
        handleTextContent(event as TextMessageContentEvent)
        break
      case EventType.TEXT_MESSAGE_END:
        handleTextEnd(event as TextMessageEndEvent)
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
        handleToolResult(event as ToolCallResultEvent)
        break
      case EventType.STEP_STARTED:
        handleStepStarted(event as StepStartedEvent)
        break
      case EventType.STEP_CONTENT:
        handleStepContent(event as StepContentEvent)
        break
      case EventType.STEP_FINISHED:
        handleStepFinished(event as StepFinishedEvent)
        break
    }
  }

  // Event handlers
  function handleRunStarted(event: RunStartedEvent) {
    isRunning.value = true
    currentRunId.value = event.run_id
    error.value = null
    steps.length = 0
    toolCalls.clear()
    messageContents.clear()
    options.onRunStart?.(event)
  }

  function handleRunFinished(event: RunFinishedEvent) {
    isRunning.value = false
    isStreaming.value = false
    currentRunId.value = null
    options.onRunFinish?.(event)
  }

  function handleRunError(event: RunErrorEvent) {
    isRunning.value = false
    isStreaming.value = false
    error.value = event.message
    options.onRunError?.(event)
  }

  function handleTextStart(event: TextMessageStartEvent) {
    isStreaming.value = true
    currentMessageId.value = event.message_id
    currentMessage.value = ''
    messageContents.set(event.message_id, '')
    options.onTextStart?.(event)
  }

  function handleTextContent(event: TextMessageContentEvent) {
    currentMessage.value += event.delta
    const existing = messageContents.get(event.message_id) || ''
    messageContents.set(event.message_id, existing + event.delta)
    options.onTextContent?.(event)
  }

  function handleTextEnd(event: TextMessageEndEvent) {
    isStreaming.value = false
    currentMessageId.value = null
    options.onTextEnd?.(event)
  }

  function handleToolStart(event: ToolCallStartEvent) {
    toolCalls.set(event.tool_call_id, {
      id: event.tool_call_id,
      name: event.tool_call_name,
      arguments: '',
      status: 'running'
    })
    options.onToolStart?.(event)
  }

  function handleToolArgs(event: ToolCallArgsEvent) {
    const call = toolCalls.get(event.tool_call_id)
    if (call) {
      call.arguments += event.delta
    }
    options.onToolArgs?.(event)
  }

  function handleToolEnd(event: ToolCallEndEvent) {
    const call = toolCalls.get(event.tool_call_id)
    if (call) {
      call.status = 'pending' // Waiting for result
    }
    options.onToolEnd?.(event)
  }

  function handleToolResult(event: ToolCallResultEvent) {
    const call = toolCalls.get(event.tool_call_id)
    if (call) {
      call.result = event.content
      call.status = 'completed'
    }
    options.onToolResult?.(event)
  }

  function handleStepStarted(event: StepStartedEvent) {
    currentStep.value = event.step_name
    steps.push({
      name: event.step_name,
      status: 'running',
      startTime: event.timestamp,
      content: '' // Initialize empty content
    })
    options.onStepStart?.(event)
  }

  function handleStepContent(event: StepContentEvent) {
    // Find the running step and append content
    const step = steps.find(s => s.name === event.step_name && s.status === 'running')
    if (step) {
      step.content = (step.content || '') + event.delta
    }
    options.onStepContent?.(event)
  }

  function handleStepFinished(event: StepFinishedEvent) {
    const step = steps.find(s => s.name === event.step_name && s.status === 'running')
    if (step) {
      step.status = 'completed'
      step.endTime = event.timestamp
    }
    currentStep.value = null
    options.onStepFinish?.(event)
  }

  /**
   * Run the agent with the given input
   */
  async function run(input: RunAgentInput): Promise<void> {
    // Reset state
    error.value = null
    isRunning.value = true

    // Create abort controller
    abortController.value = new AbortController()

    const baseUrl = import.meta.env.VITE_API_URL || '/api/v1'
    const url = `${baseUrl}/agent/run`

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${authStore.token}`,
          Accept: 'text/event-stream'
        },
        body: JSON.stringify(input),
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
              handleEvent(event)
            } catch (e) {
              console.error('Failed to parse event:', e)
            }
            currentEventType = ''
            currentEventData = ''
          }
        }
      }
    } catch (e) {
      if ((e as Error).name === 'AbortError') {
        error.value = 'Run was cancelled'
      } else {
        error.value = (e as Error).message
      }
    } finally {
      isRunning.value = false
      isStreaming.value = false
      abortController.value = null
    }
  }

  /**
   * Send a message to the agent
   */
  async function sendMessage(
    threadId: string,
    content: string,
    existingMessages: Message[] = [],
    agentConfig?: {
      agentType?: string
      modelId?: string
      temperature?: number
      maxTokens?: number
      systemPrompt?: string
    },
    tools?: Tool[]
  ): Promise<void> {
    // Create user message
    const userMessage = {
      id: `msg-${Date.now()}`,
      role: 'user' as const,
      content
    }

    // Build messages array
    const messages = [
      ...existingMessages.map(m => ({
        id: m.id,
        role: m.role,
        content: m.content
      })),
      userMessage
    ]

    // Build input
    const input: RunAgentInput = {
      thread_id: threadId,
      messages,
      tools: tools ?? [],
      forwarded_props: {
        agent_type: agentConfig?.agentType ?? 'react',
        model_id: agentConfig?.modelId,
        temperature: agentConfig?.temperature ?? 0.7,
        max_tokens: agentConfig?.maxTokens ?? 4096,
        system_prompt: agentConfig?.systemPrompt
      }
    }

    await run(input)
  }

  /**
   * Abort the current run
   */
  function abort() {
    if (abortController.value) {
      abortController.value.abort()
      abortController.value = null
    }
  }

  /**
   * Stop the run via API
   */
  async function stop(): Promise<boolean> {
    if (!currentRunId.value) {
      return false
    }

    const baseUrl = import.meta.env.VITE_API_URL || '/api/v1'
    const url = `${baseUrl}/agent/run/${currentRunId.value}/stop`

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${authStore.token}`
        }
      })

      if (response.ok) {
        const data = await response.json()
        return data.data?.stopped ?? false
      }
    } catch (e) {
      console.error('Failed to stop run:', e)
    }

    // Also abort locally
    abort()
    return true
  }

  /**
   * Get content for a specific message ID
   */
  function getMessageContent(messageId: string): string {
    return messageContents.get(messageId) || ''
  }

  /**
   * Get tool call by ID
   */
  function getToolCall(toolCallId: string): ToolCall | undefined {
    return toolCalls.get(toolCallId)
  }

  /**
   * Reset state
   */
  function reset() {
    isRunning.value = false
    isStreaming.value = false
    currentRunId.value = null
    error.value = null
    currentStep.value = null
    currentMessageId.value = null
    currentMessage.value = ''
    steps.length = 0
    toolCalls.clear()
    messageContents.clear()
  }

  return {
    // State
    isRunning,
    isStreaming,
    currentRunId,
    error,
    currentStep,
    steps,
    currentMessageId,
    currentMessage,
    toolCalls,
    canAbort,

    // Methods
    run,
    sendMessage,
    abort,
    stop,
    getMessageContent,
    getToolCall,
    reset,
    handleEvent
  }
}

export type UseAgentChatReturn = ReturnType<typeof useAgentChat>
