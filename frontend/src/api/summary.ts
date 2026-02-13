/**
 * Summary API Client
 *
 * Provides API functions for AI summary feature including:
 * - Summary CRUD operations
 * - Industry list
 * - Summary generation (SSE streaming)
 */

const API_BASE_URL = '/api/summary'

// ==================== Type Definitions ====================

/**
 * Summary data
 */
export interface Summary {
  id: number
  industry: string
  record_ids: string[]
  content: string
  record_count: number
  created_at: string
  updated_at: string
}

/**
 * Summary generation request
 */
export interface SummaryGenerateRequest {
  industry: string
  record_ids: string[]
}

/**
 * Summary generation progress event
 */
export interface SummaryProgressEvent {
  step: string
  message: string
}

/**
 * Summary generation complete event
 */
export interface SummaryCompleteEvent {
  id: number
  industry: string
  content: string
}

/**
 * Summary generation error event
 */
export interface SummaryErrorEvent {
  error: string
}

/**
 * Summary generation finish event
 */
export interface SummaryFinishEvent {
  record_ids: string[]
}

/**
 * API response wrapper
 */
export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  count?: number
  message?: string
  error?: string
}

// ==================== API Functions ====================

/**
 * Get all summaries
 *
 * @param industry - Optional industry filter
 * @returns Promise with summaries list
 */
export async function getAllSummaries(industry?: string): Promise<ApiResponse<Summary[]>> {
  try {
    const url = industry
      ? `${API_BASE_URL}?industry=${encodeURIComponent(industry)}`
      : API_BASE_URL

    const response = await fetch(url, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' }
    })
    const data = await response.json()

    return {
      success: data.success,
      data: data.data || [],
      count: data.count,
      error: data.error
    }
  } catch (error: any) {
    console.error('[Summary API] Failed to get all summaries:', error)
    return {
      success: false,
      data: [],
      error: '网络连接失败，请检查网络设置'
    }
  }
}

/**
 * Get industries with summaries
 *
 * @returns Promise with industries list
 */
export async function getIndustries(): Promise<ApiResponse<string[]>> {
  try {
    const response = await fetch(`${API_BASE_URL}/industries`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' }
    })
    const data = await response.json()

    return {
      success: data.success,
      data: data.data || [],
      count: data.count,
      error: data.error
    }
  } catch (error: any) {
    console.error('[Summary API] Failed to get industries:', error)
    return {
      success: false,
      data: [],
      error: '网络连接失败，请检查网络设置'
    }
  }
}

/**
 * Get single summary by ID
 *
 * @param summaryId - The summary ID
 * @returns Promise with summary data
 */
export async function getSummary(summaryId: number): Promise<ApiResponse<Summary>> {
  try {
    const response = await fetch(`${API_BASE_URL}/${summaryId}`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' }
    })
    const data = await response.json()

    return {
      success: data.success,
      data: data.data,
      error: data.error
    }
  } catch (error: any) {
    console.error('[Summary API] Failed to get summary:', error)
    return {
      success: false,
      error: '网络连接失败，请检查网络设置'
    }
  }
}

/**
 * Delete summary by ID
 *
 * @param summaryId - The summary ID to delete
 * @returns Promise with success status
 */
export async function deleteSummary(summaryId: number): Promise<ApiResponse<void>> {
  try {
    const response = await fetch(`${API_BASE_URL}/${summaryId}`, {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' }
    })
    const data = await response.json()

    return {
      success: data.success,
      message: data.message,
      error: data.error
    }
  } catch (error: any) {
    console.error('[Summary API] Failed to delete summary:', error)
    return {
      success: false,
      error: '网络连接失败，请检查网络设置'
    }
  }
}

/**
 * Generate summary (SSE streaming)
 *
 * @param request - The generation request
 * @param callbacks - Object containing event callbacks
 */
export async function generateSummaryStream(
  request: SummaryGenerateRequest,
  callbacks: {
    onProgress?: (data: SummaryProgressEvent) => void
    onComplete?: (data: SummaryCompleteEvent) => void
    onError?: (data: SummaryErrorEvent) => void
    onFinish?: (data: SummaryFinishEvent) => void
    onStreamError?: (error: Error) => void
  }
): Promise<void> {
  try {
    const response = await fetch(`${API_BASE_URL}/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request)
    })

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }

    const reader = response.body?.getReader()
    if (!reader) {
      throw new Error('Response body is not readable')
    }

    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (!line.trim()) continue

        const [eventLine, dataLine] = line.split('\n')
        if (!eventLine || !dataLine) continue

        const eventType = eventLine.replace('event: ', '').trim()
        const eventData = dataLine.replace('data: ', '').trim()

        try {
          const data = JSON.parse(eventData)

          switch (eventType) {
            case 'progress':
              callbacks.onProgress?.(data)
              break
            case 'complete':
              callbacks.onComplete?.(data)
              break
            case 'error':
              callbacks.onError?.(data)
              break
            case 'finish':
              callbacks.onFinish?.(data)
              break
          }
        } catch (parseError) {
          console.error('[SSE] Failed to parse event:', parseError, eventData)
        }
      }
    }
  } catch (error) {
    callbacks.onStreamError?.(error as Error)
  }
}
