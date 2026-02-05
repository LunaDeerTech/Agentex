/* eslint-disable @typescript-eslint/no-explicit-any */
import request from './request'

// ============== Types ==============

export type LLMProvider = 'openai' | 'anthropic'

export interface LLMModel {
  id: string
  name: string
  provider: string
  model_id: string
  base_url: string | null
  api_key_masked: string
  max_tokens: number
  temperature: number
  top_p: number
  is_enabled: boolean
  is_default: boolean
  description: string | null
  created_at: string
  updated_at: string
}

export interface LLMModelListResponse {
  models: LLMModel[]
  total: number
}

export interface LLMModelCreateRequest {
  name: string
  provider: LLMProvider
  model_id: string
  api_key: string
  base_url?: string
  max_tokens?: number
  temperature?: number
  top_p?: number
  is_default?: boolean
  description?: string
}

export interface LLMModelUpdateRequest {
  name?: string
  model_id?: string
  api_key?: string
  base_url?: string
  max_tokens?: number
  temperature?: number
  top_p?: number
  is_enabled?: boolean
  is_default?: boolean
  description?: string
}

export interface LLMModelTestRequest {
  prompt?: string
}

export interface LLMModelTestResponse {
  success: boolean
  message: string
  response_text: string | null
  latency_ms: number | null
  model_info: Record<string, any> | null
}

export interface OperationStatus {
  message: string
}

// ============== API Functions ==============

/**
 * Create a new LLM model configuration
 */
export const createModel = (data: LLMModelCreateRequest) => {
  return request.post<LLMModel>('/models', data)
}

/**
 * List all LLM model configurations for the current user
 */
export const listModels = () => {
  return request.get<LLMModelListResponse>('/models')
}

/**
 * Get a specific LLM model configuration
 */
export const getModel = (modelId: string) => {
  return request.get<LLMModel>(`/models/${modelId}`)
}

/**
 * Update an LLM model configuration
 */
export const updateModel = (modelId: string, data: LLMModelUpdateRequest) => {
  return request.put<LLMModel>(`/models/${modelId}`, data)
}

/**
 * Delete an LLM model configuration
 */
export const deleteModel = (modelId: string) => {
  return request.delete<OperationStatus>(`/models/${modelId}`)
}

/**
 * Test an LLM model configuration
 */
export const testModel = (modelId: string, data?: LLMModelTestRequest) => {
  return request.post<LLMModelTestResponse>(`/models/${modelId}/test`, data || {})
}

/**
 * Set a model as the default
 */
export const setDefaultModel = (modelId: string) => {
  return request.post<LLMModel>(`/models/${modelId}/set-default`)
}

/**
 * Get the default LLM model
 */
export const getDefaultModel = () => {
  return request.get<LLMModel>('/models/default')
}

// ============== Helpers ==============

export const PROVIDER_OPTIONS = [
  { value: 'openai', label: 'OpenAI', icon: '🤖' },
  { value: 'anthropic', label: 'Anthropic', icon: '🔮' }
] as const

export const MODEL_PRESETS: Record<LLMProvider, { value: string; label: string }[]> = {
  openai: [
    { value: 'gpt-4o', label: 'GPT-4o' },
    { value: 'gpt-4o-mini', label: 'GPT-4o Mini' },
    { value: 'gpt-4-turbo', label: 'GPT-4 Turbo' },
    { value: 'gpt-4', label: 'GPT-4' },
    { value: 'gpt-3.5-turbo', label: 'GPT-3.5 Turbo' },
    { value: 'o1', label: 'o1' },
    { value: 'o1-mini', label: 'o1 Mini' }
  ],
  anthropic: [
    { value: 'claude-sonnet-4-20250514', label: 'Claude Sonnet 4' },
    { value: 'claude-3-7-sonnet-20250219', label: 'Claude 3.7 Sonnet' },
    { value: 'claude-3-5-sonnet-20241022', label: 'Claude 3.5 Sonnet' },
    { value: 'claude-3-5-haiku-20241022', label: 'Claude 3.5 Haiku' },
    { value: 'claude-3-opus-20240229', label: 'Claude 3 Opus' }
  ]
}

export const getProviderLabel = (provider: string): string => {
  return PROVIDER_OPTIONS.find(p => p.value === provider)?.label || provider
}

export const getProviderIcon = (provider: string): string => {
  return PROVIDER_OPTIONS.find(p => p.value === provider)?.icon || '🔌'
}
