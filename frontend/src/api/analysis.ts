/**
 * Analysis API Client
 *
 * Provides API functions for the analysis feature including:
 * - Draft management (get, save)
 * - Analysis submission
 * - Visual description generation
 */

import type { Comment } from '@/types/analysis'

const API_BASE_URL = '/api/analysis'

// ==================== Type Definitions ====================

/**
 * Analysis draft data
 */
export interface AnalysisDraft {
  id: string
  record_id: string
  status: 'draft' | 'analyzing' | 'completed'
  industry: string
  follower_count: number
  published_at: string | null
  likes_count: number
  saves_count: number
  comments_count: number
  title: string
  content: string
  visual_description: string
  top_comments: Comment[]
  // NEW: Image description tracking
  image_descriptions?: Record<number, {
    id: string
    content: string
  }>
  generated_image_indices?: number[]
  created_at?: string
  updated_at?: string
}

/**
 * Visual description request
 */
export interface VisualDescriptionRequest {
  record_id: string
  image_indices: number[]  // -1 for cover, 0,1,2... for content images
}

/**
 * Visual description response
 */
export interface VisualDescriptionResponse {
  description: string
}

/**
 * Image proxy upload response
 */
export interface ImageProxyUploadResponse {
  success: boolean
  url?: string
  error?: string
}

/**
 * API response wrapper
 */
export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  message?: string
  error?: string
}

// ==================== API Functions ====================

/**
 * Get draft data for a specific record
 *
 * @param recordId - The record ID to get draft for
 * @returns Promise with draft data or null
 */
export async function getDraft(recordId: string): Promise<ApiResponse<AnalysisDraft | null>> {
  try {
    const response = await fetch(`${API_BASE_URL}/draft?record_id=${encodeURIComponent(recordId)}`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' }
    })
    const data = await response.json()

    return {
      success: data.success,
      data: data.data || null,
      error: data.error
    }
  } catch (error: any) {
    console.error('[Analysis API] Failed to get draft:', error)
    return {
      success: false,
      data: null,
      error: '网络连接失败，请检查网络设置'
    }
  }
}

/**
 * Save draft data
 *
 * @param draftData - The draft data to save
 * @returns Promise with saved draft data
 */
export async function saveDraft(draftData: Partial<AnalysisDraft>): Promise<ApiResponse<AnalysisDraft>> {
  try {
    const response = await fetch(`${API_BASE_URL}/draft`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(draftData)
    })
    const data = await response.json()

    return {
      success: data.success,
      data: data.data,
      message: data.message,
      error: data.error
    }
  } catch (error: any) {
    console.error('[Analysis API] Failed to save draft:', error)
    return {
      success: false,
      error: '保存失败，请检查网络连接'
    }
  }
}

/**
 * Submit analysis
 *
 * @param draftData - The analysis data to submit
 * @returns Promise with submitted data
 */
export async function submitAnalysis(draftData: Partial<AnalysisDraft>): Promise<ApiResponse<AnalysisDraft>> {
  try {
    const response = await fetch(`${API_BASE_URL}/submit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(draftData)
    })
    const data = await response.json()

    return {
      success: data.success,
      data: data.data,
      message: data.message,
      error: data.error
    }
  } catch (error: any) {
    console.error('[Analysis API] Failed to submit analysis:', error)
    return {
      success: false,
      error: '提交失败，请检查网络连接'
    }
  }
}

/**
 * AI analysis stream (SSE)
 *
 * @param recordId - The record ID to analyze
 * @param draftData - The draft data for analysis
 * @param callbacks - Object containing event callbacks
 */
export async function analyzeStream(
  recordId: string,
  draftData: Partial<AnalysisDraft>,
  callbacks: {
    onProgress: (data: { status: string; message: string; step?: string }) => void
    onComplete: (data: { record_id: string; content: string }) => void
    onError: (data: { record_id: string; error: string }) => void
    onFinish: (data: { record_id: string }) => void
    onStreamError: (error: Error) => void
  }
): Promise<void> {
  try {
    const response = await fetch(`${API_BASE_URL}/analyze-stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ record_id: recordId, draft_data: draftData })
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
              callbacks.onProgress(data)
              break
            case 'complete':
              callbacks.onComplete(data)
              break
            case 'error':
              callbacks.onError(data)
              break
            case 'finish':
              callbacks.onFinish(data)
              break
          }
        } catch (parseError) {
          console.error('[SSE] Failed to parse event:', parseError, eventData)
        }
      }
    }
  } catch (error) {
    callbacks.onStreamError(error as Error)
  }
}

/**
 * Generate visual description using AI
 *
 * @param request - The visual description request
 * @returns Promise with generated description
 */
export async function generateVisualDescription(
  request: VisualDescriptionRequest
): Promise<ApiResponse<VisualDescriptionResponse>> {
  try {
    const response = await fetch(`${API_BASE_URL}/visual-desc`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request)
    })
    const data = await response.json()

    if (data.success && data.data) {
      return {
        success: true,
        data: {
          description: data.data.description || ''
        }
      }
    }

    return {
      success: false,
      error: data.error || 'AI 生成失败'
    }
  } catch (error: any) {
    console.error('[Analysis API] Failed to generate visual description:', error)
    return {
      success: false,
      error: '网络连接失败，请检查网络设置'
    }
  }
}

/**
 * Get analysis result for a specific record
 *
 * @param recordId - The record ID to get result for
 * @returns Promise with analysis result
 */
export async function getAnalysisResult(recordId: string): Promise<ApiResponse<any>> {
  try {
    const response = await fetch(`${API_BASE_URL}/result/${encodeURIComponent(recordId)}`, {
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
    console.error('[Analysis API] Failed to get analysis result:', error)
    return {
      success: false,
      error: '网络连接失败，请检查网络设置'
    }
  }
}

/**
 * Get all analysis results
 *
 * @returns Promise with all analysis results
 */
export async function getAllAnalysisResults(): Promise<ApiResponse<any[]>> {
  try {
    const response = await fetch(`${API_BASE_URL}/results`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' }
    })
    const data = await response.json()

    return {
      success: data.success,
      data: data.data || [],
      error: data.error
    }
  } catch (error: any) {
    console.error('[Analysis API] Failed to get all analysis results:', error)
    return {
      success: false,
      data: [],
      error: '网络连接失败，请检查网络设置'
    }
  }
}

// ==================== Image Proxy Upload API ====================

/**
 * Upload image to image proxy service
 *
 * @param file - Image file to upload
 * @returns Promise with upload response
 */
export async function uploadImageToProxy(file: File): Promise<ImageProxyUploadResponse> {
  try {
    const formData = new FormData()
    formData.append('file', file)

    const response = await fetch('/api/image-proxy/upload', {
      method: 'POST',
      body: formData
    })

    const data = await response.json()

    return {
      success: response.ok,
      url: data.url,
      error: data.error
    }
  } catch (error: any) {
    console.error('[Image Proxy API] Upload failed:', error)
    return {
      success: false,
      error: '上传失败，请检查网络连接'
    }
  }
}
