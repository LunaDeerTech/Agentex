/**
 * Session API module
 * Handles all session and message related API calls
 */

import request from './request'

// ============ Types ============

export interface SessionSettings {
  temperature?: number
  max_tokens?: number
  system_prompt?: string
  knowledge_base_ids?: string[]
  mcp_connection_ids?: string[]
  skill_ids?: string[]
}

export interface Session {
  id: string
  user_id: string
  title: string | null
  agent_type: 'react' | 'agentic_rag' | 'plan_execute'
  model_config_id: string | null
  settings: SessionSettings
  created_at: string
  updated_at: string
}

export interface SessionCreateParams {
  title?: string
  agent_type?: 'react' | 'agentic_rag' | 'plan_execute'
  model_config_id?: string
  settings?: SessionSettings
}

export interface SessionUpdateParams {
  title?: string
  agent_type?: 'react' | 'agentic_rag' | 'plan_execute'
  model_config_id?: string
  settings?: SessionSettings
}

export interface SessionListResponse {
  items: Session[]
  total: number
  page: number
  page_size: number
}

export interface Message {
  id: string
  session_id: string
  role: 'user' | 'assistant' | 'system' | 'tool'
  content: string
  meta: Record<string, unknown>
  created_at: string
}

export interface MessageCreateParams {
  role: 'user' | 'assistant' | 'system' | 'tool'
  content: string
  meta?: Record<string, unknown>
}

export interface MessageListResponse {
  items: Message[]
  total: number
  page: number
  page_size: number
}

// ============ Session API ============

/**
 * Create a new session
 */
export function createSession(params: SessionCreateParams = {}): Promise<Session> {
  return request.post('/sessions', params)
}

/**
 * Get list of sessions
 */
export function getSessions(page = 1, pageSize = 20): Promise<SessionListResponse> {
  return request.get('/sessions', {
    params: { page, page_size: pageSize }
  })
}

/**
 * Get session by ID
 */
export function getSession(sessionId: string): Promise<Session> {
  return request.get(`/sessions/${sessionId}`)
}

/**
 * Update session
 */
export function updateSession(sessionId: string, params: SessionUpdateParams): Promise<Session> {
  return request.put(`/sessions/${sessionId}`, params)
}

/**
 * Delete session
 */
export function deleteSession(sessionId: string): Promise<void> {
  return request.delete(`/sessions/${sessionId}`)
}

// ============ Message API ============

/**
 * Get messages for a session
 */
export function getMessages(
  sessionId: string,
  page = 1,
  pageSize = 50
): Promise<MessageListResponse> {
  return request.get(`/sessions/${sessionId}/messages`, {
    params: { page, page_size: pageSize }
  })
}

/**
 * Create a new message in a session
 */
export function createMessage(sessionId: string, params: MessageCreateParams): Promise<Message> {
  return request.post(`/sessions/${sessionId}/messages`, params)
}
