/**
 * 对标文案查询相关 API
 *
 * 提供飞书多维表格数据查询功能，包括：
 * - 记录列表查询（分页、筛选、排序）
 * - 记录详情获取
 * - 统计信息
 * - 数据同步
 * - 飞书配置管理
 */

import axios from 'axios'

const API_BASE_URL = '/api'

// ==================== 类型定义 ====================

/**
 * 博主信息
 */
export interface BloggerInfo {
  nickname: string
  blogger_id: string
  homepage: string
  avatar: string
  bio: string
  follower_count: number
}

/**
 * 笔记指标
 */
export interface NoteMetrics {
  likes: number
  saves: number
  comments: number
  total_engagement: number
  save_ratio: number
  comment_ratio: number
}

/**
 * 对标文案记录
 */
export interface ReferenceRecord {
  record_id: string
  keyword: string
  blogger: BloggerInfo
  title: string
  body: string
  cover_image: string
  images: string[]
  tags: string[]
  note_link: string
  metrics: NoteMetrics
  category: string
  industry: string
  note_type: string
  created_at: string | null
  updated_at: string | null
}

/**
 * 查询参数
 */
export interface ReferenceQueryParams {
  page?: number
  page_size?: number
  keyword?: string
  industry?: string
  note_type?: string
  min_likes?: number
  min_saves?: number
  sort_by?: 'created_at' | 'likes' | 'saves' | 'comments' | 'total_engagement' | 'save_ratio'
  sort_order?: 'asc' | 'desc'
}

/**
 * 查询结果
 */
export interface ReferenceQueryResult {
  success: boolean
  records: ReferenceRecord[]
  total: number
  page: number
  page_size: number
  has_more: boolean
  error?: string
}

/**
 * 统计信息
 */
export interface ReferenceStats {
  success: boolean
  total_records: number
  industry_distribution: Record<string, number>
  note_type_distribution: Record<string, number>
  avg_likes: number
  avg_saves: number
  avg_comments: number
  error?: string
}

/**
 * 飞书工作区配置
 */
export interface FeishuWorkspace {
  name: string
  app_id: string
  app_secret: string
  base_url: string
  user_access_token: string
  cache_enabled: boolean
  cache_ttl: number
}

/**
 * 飞书配置
 */
export interface FeishuConfig {
  active_workspace: string
  workspaces: Record<string, FeishuWorkspace>
}

// ==================== API 函数 ====================

/**
 * 获取对标文案记录列表
 *
 * 支持分页、关键词搜索、行业筛选、笔记类型筛选、点赞/收藏数筛选、排序
 *
 * @param params - 查询参数
 * @returns Promise 包含记录列表和分页信息
 */
export async function getReferenceRecords(
  params: ReferenceQueryParams = {}
): Promise<ReferenceQueryResult> {
  try {
    const queryParams: Record<string, any> = {
      page: params.page || 1,
      page_size: params.page_size || 20
    }

    if (params.keyword) queryParams.keyword = params.keyword
    if (params.industry) queryParams.industry = params.industry
    if (params.note_type) queryParams.note_type = params.note_type
    if (params.min_likes !== undefined) queryParams.min_likes = params.min_likes
    if (params.min_saves !== undefined) queryParams.min_saves = params.min_saves
    if (params.sort_by) queryParams.sort_by = params.sort_by
    if (params.sort_order) queryParams.sort_order = params.sort_order

    const response = await axios.get<{ success: boolean; records: ReferenceRecord[]; total: number; page: number; page_size: number; has_more: boolean }>(
      `${API_BASE_URL}/reference/records`,
      {
        params: queryParams,
        timeout: 30000 // 30秒超时
      }
    )

    return {
      success: response.data.success,
      records: response.data.records || [],
      total: response.data.total || 0,
      page: response.data.page || 1,
      page_size: response.data.page_size || 20,
      has_more: response.data.has_more || false
    }
  } catch (error: any) {
    if (axios.isAxiosError(error)) {
      if (error.code === 'ECONNABORTED') {
        return {
          success: false,
          records: [],
          total: 0,
          page: 1,
          page_size: params.page_size || 20,
          has_more: false,
          error: '请求超时，请检查网络连接'
        }
      }
      if (!error.response) {
        return {
          success: false,
          records: [],
          total: 0,
          page: 1,
          page_size: params.page_size || 20,
          has_more: false,
          error: '网络连接失败，请检查网络设置'
        }
      }
      const errorMessage = error.response?.data?.error || error.message || '获取对标文案列表失败'
      return {
        success: false,
        records: [],
        total: 0,
        page: 1,
        page_size: params.page_size || 20,
        has_more: false,
        error: errorMessage
      }
    }
    return {
      success: false,
      records: [],
      total: 0,
      page: 1,
      page_size: params.page_size || 20,
      has_more: false,
      error: '未知错误，请稍后重试'
    }
  }
}

/**
 * 获取单条对标文案记录详情
 *
 * @param recordId - 记录 ID
 * @returns Promise 包含记录详细信息
 */
export async function getReferenceRecord(
  recordId: string
): Promise<{ success: boolean; record?: ReferenceRecord; error?: string }> {
  try {
    const response = await axios.get<{ success: boolean; record: ReferenceRecord }>(
      `${API_BASE_URL}/reference/records/${recordId}`,
      {
        timeout: 10000 // 10秒超时
      }
    )
    return {
      success: response.data.success,
      record: response.data.record,
      error: undefined
    }
  } catch (error: any) {
    if (axios.isAxiosError(error)) {
      if (error.code === 'ECONNABORTED') {
        return { success: false, error: '请求超时，请检查网络连接' }
      }
      if (!error.response) {
        return { success: false, error: '网络连接失败，请检查网络设置' }
      }
      if (error.response.status === 404) {
        return { success: false, error: '对标文案记录不存在' }
      }
      const errorMessage = error.response?.data?.error || error.message || '获取对标文案详情失败'
      return { success: false, error: errorMessage }
    }
    return { success: false, error: '未知错误，请稍后重试' }
  }
}

/**
 * 获取对标文案统计信息
 *
 * @returns Promise 包含统计数据
 */
export async function getReferenceStats(): Promise<ReferenceStats> {
  try {
    const response = await axios.get<{
      success: boolean
      total_records: number
      industry_distribution: Record<string, number>
      note_type_distribution: Record<string, number>
      avg_likes: number
      avg_saves: number
      avg_comments: number
    }>(
      `${API_BASE_URL}/reference/stats`,
      {
        timeout: 10000 // 10秒超时
      }
    )

    return {
      success: response.data.success,
      total_records: response.data.total_records || 0,
      industry_distribution: response.data.industry_distribution || {},
      note_type_distribution: response.data.note_type_distribution || {},
      avg_likes: response.data.avg_likes || 0,
      avg_saves: response.data.avg_saves || 0,
      avg_comments: response.data.avg_comments || 0
    }
  } catch (error: any) {
    if (axios.isAxiosError(error)) {
      if (error.code === 'ECONNABORTED') {
        return {
          success: false,
          total_records: 0,
          industry_distribution: {},
          note_type_distribution: {},
          avg_likes: 0,
          avg_saves: 0,
          avg_comments: 0,
          error: '请求超时，请检查网络连接'
        }
      }
      if (!error.response) {
        return {
          success: false,
          total_records: 0,
          industry_distribution: {},
          note_type_distribution: {},
          avg_likes: 0,
          avg_saves: 0,
          avg_comments: 0,
          error: '网络连接失败，请检查网络设置'
        }
      }
      const errorMessage = error.response?.data?.error || error.message || '获取统计信息失败'
      return {
        success: false,
        total_records: 0,
        industry_distribution: {},
        note_type_distribution: {},
        avg_likes: 0,
        avg_saves: 0,
        avg_comments: 0,
        error: errorMessage
      }
    }
    return {
      success: false,
      total_records: 0,
      industry_distribution: {},
      note_type_distribution: {},
      avg_likes: 0,
      avg_saves: 0,
      avg_comments: 0,
      error: '未知错误，请稍后重试'
    }
  }
}

/**
 * 同步飞书数据
 *
 * 清除缓存并从飞书重新获取数据
 *
 * @returns Promise 包含同步结果
 */
export async function syncReferenceData(): Promise<{
  success: boolean
  message?: string
  count?: number
  synced_at?: string
  error?: string
}> {
  try {
    const response = await axios.post<{
      success: boolean
      message: string
      count: number
      synced_at: string
    }>(
      `${API_BASE_URL}/reference/sync`,
      {},
      {
        timeout: 60000 // 60秒超时，同步可能需要较长时间
      }
    )

    return {
      success: response.data.success,
      message: response.data.message,
      count: response.data.count,
      synced_at: response.data.synced_at
    }
  } catch (error: any) {
    if (axios.isAxiosError(error)) {
      if (error.code === 'ECONNABORTED') {
        return { success: false, error: '请求超时，请检查网络连接' }
      }
      if (!error.response) {
        return { success: false, error: '网络连接失败，请检查网络设置' }
      }
      const errorMessage = error.response?.data?.error || error.message || '同步数据失败'
      return { success: false, error: errorMessage }
    }
    return { success: false, error: '未知错误，请稍后重试' }
  }
}

/**
 * 获取飞书配置（敏感信息已脱敏）
 *
 * @returns Promise 包含飞书配置
 */
export async function getFeishuConfig(): Promise<{
  success: boolean
  config?: FeishuConfig
  error?: string
}> {
  try {
    const response = await axios.get<{ success: boolean; config: FeishuConfig }>(
      `${API_BASE_URL}/reference/config`,
      {
        timeout: 10000 // 10秒超时
      }
    )

    return {
      success: response.data.success,
      config: response.data.config
    }
  } catch (error: any) {
    if (axios.isAxiosError(error)) {
      if (error.code === 'ECONNABORTED') {
        return { success: false, error: '请求超时，请检查网络连接' }
      }
      if (!error.response) {
        return { success: false, error: '网络连接失败，请检查网络设置' }
      }
      const errorMessage = error.response?.data?.error || error.message || '获取飞书配置失败'
      return { success: false, error: errorMessage }
    }
    return { success: false, error: '未知错误，请稍后重试' }
  }
}

/**
 * 更新飞书配置
 *
 * @param config - 完整的飞书配置
 * @returns Promise 包含操作结果
 */
export async function updateFeishuConfig(
  config: FeishuConfig
): Promise<{ success: boolean; message?: string; error?: string }> {
  try {
    const response = await axios.post<{ success: boolean; message: string }>(
      `${API_BASE_URL}/reference/config`,
      config,
      {
        timeout: 10000 // 10秒超时
      }
    )

    return {
      success: response.data.success,
      message: response.data.message
    }
  } catch (error: any) {
    if (axios.isAxiosError(error)) {
      if (error.code === 'ECONNABORTED') {
        return { success: false, error: '请求超时，请检查网络连接' }
      }
      if (!error.response) {
        return { success: false, error: '网络连接失败，请检查网络设置' }
      }
      const errorMessage = error.response?.data?.error || error.message || '更新飞书配置失败'
      return { success: false, error: errorMessage }
    }
    return { success: false, error: '未知错误，请稍后重试' }
  }
}

/**
 * 测试飞书连接
 *
 * @param config - 飞书连接配置
 * @returns Promise 包含测试结果
 */
export async function testFeishuConnection(
  config: {
    app_id: string
    app_secret: string
    user_access_token?: string
    base_url: string
  }
): Promise<{
  success: boolean
  message?: string
  tables?: string[]
  app_token?: string
  error?: string
}> {
  try {
    const response = await axios.post<{
      success: boolean
      message: string
      tables: string[]
      app_token: string
    }>(
      `${API_BASE_URL}/reference/config/test`,
      config,
      {
        timeout: 30000 // 30秒超时
      }
    )

    if (response.data.success) {
      return {
        success: true,
        message: response.data.message,
        tables: response.data.tables,
        app_token: response.data.app_token
      }
    } else {
      return {
        success: false,
        error: response.data.error || '连接失败'
      }
    }
  } catch (error: any) {
    if (axios.isAxiosError(error)) {
      if (error.code === 'ECONNABORTED') {
        return { success: false, error: '请求超时，请检查网络连接' }
      }
      if (!error.response) {
        return { success: false, error: '网络连接失败，请检查网络设置' }
      }
      const errorMessage = error.response?.data?.error || error.message || '测试飞书连接失败'
      return { success: false, error: errorMessage }
    }
    return { success: false, error: '未知错误，请稍后重试' }
  }
}
