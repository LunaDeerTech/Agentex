/**
 * AG-UI Event Types
 *
 * TypeScript definitions for Agent-User Interaction Protocol events
 */

// Event types enum
export enum EventType {
  // Lifecycle events
  RUN_STARTED = 'RUN_STARTED',
  RUN_FINISHED = 'RUN_FINISHED',
  RUN_ERROR = 'RUN_ERROR',

  // Text message events
  TEXT_MESSAGE_START = 'TEXT_MESSAGE_START',
  TEXT_MESSAGE_CONTENT = 'TEXT_MESSAGE_CONTENT',
  TEXT_MESSAGE_END = 'TEXT_MESSAGE_END',

  // Tool call events
  TOOL_CALL_START = 'TOOL_CALL_START',
  TOOL_CALL_ARGS = 'TOOL_CALL_ARGS',
  TOOL_CALL_END = 'TOOL_CALL_END',
  TOOL_CALL_RESULT = 'TOOL_CALL_RESULT',

  // Step events
  STEP_STARTED = 'STEP_STARTED',
  STEP_CONTENT = 'STEP_CONTENT',
  STEP_FINISHED = 'STEP_FINISHED',

  // State events
  STATE_SNAPSHOT = 'STATE_SNAPSHOT',
  STATE_DELTA = 'STATE_DELTA'
}

// Base event interface
export interface BaseEvent {
  type: EventType
  timestamp: number
}

// Lifecycle events
export interface RunStartedEvent extends BaseEvent {
  type: EventType.RUN_STARTED
  thread_id: string
  run_id: string
}

export interface RunFinishedEvent extends BaseEvent {
  type: EventType.RUN_FINISHED
  thread_id: string
  run_id: string
  result?: {
    usage?: {
      prompt_tokens?: number
      completion_tokens?: number
    }
  }
}

export interface RunErrorEvent extends BaseEvent {
  type: EventType.RUN_ERROR
  message: string
  code: string
}

// Text message events
export interface TextMessageStartEvent extends BaseEvent {
  type: EventType.TEXT_MESSAGE_START
  message_id: string
  role: string
}

export interface TextMessageContentEvent extends BaseEvent {
  type: EventType.TEXT_MESSAGE_CONTENT
  message_id: string
  delta: string
}

export interface TextMessageEndEvent extends BaseEvent {
  type: EventType.TEXT_MESSAGE_END
  message_id: string
}

// Tool call events
export interface ToolCallStartEvent extends BaseEvent {
  type: EventType.TOOL_CALL_START
  tool_call_id: string
  tool_call_name: string
  parent_message_id?: string
}

export interface ToolCallArgsEvent extends BaseEvent {
  type: EventType.TOOL_CALL_ARGS
  tool_call_id: string
  delta: string
}

export interface ToolCallEndEvent extends BaseEvent {
  type: EventType.TOOL_CALL_END
  tool_call_id: string
}

export interface ToolCallResultEvent extends BaseEvent {
  type: EventType.TOOL_CALL_RESULT
  message_id: string
  tool_call_id: string
  content: string
  role: string
}

// Step events
export interface StepStartedEvent extends BaseEvent {
  type: EventType.STEP_STARTED
  step_name: string
}

export interface StepContentEvent extends BaseEvent {
  type: EventType.STEP_CONTENT
  step_name: string
  delta: string
}

export interface StepFinishedEvent extends BaseEvent {
  type: EventType.STEP_FINISHED
  step_name: string
}

// State events
export interface StateSnapshotEvent extends BaseEvent {
  type: EventType.STATE_SNAPSHOT
  snapshot: Record<string, unknown>
}

export interface StateDeltaEvent extends BaseEvent {
  type: EventType.STATE_DELTA
  delta: Array<{ op: string; path: string; value?: unknown }>
}

// Union type for all events
export type AgentEvent =
  | RunStartedEvent
  | RunFinishedEvent
  | RunErrorEvent
  | TextMessageStartEvent
  | TextMessageContentEvent
  | TextMessageEndEvent
  | ToolCallStartEvent
  | ToolCallArgsEvent
  | ToolCallEndEvent
  | ToolCallResultEvent
  | StepStartedEvent
  | StepContentEvent
  | StepFinishedEvent
  | StateSnapshotEvent
  | StateDeltaEvent

/**
 * Parse an SSE event string into an AgentEvent object
 */
export function parseSSEEvent(eventType: string, data: string): AgentEvent | null {
  try {
    const parsed = JSON.parse(data)
    return parsed as AgentEvent
  } catch {
    console.error('Failed to parse SSE event:', eventType, data)
    return null
  }
}
