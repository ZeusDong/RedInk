/**
 * 智能推荐 V2 API
 *
 * 提供基于AI分析的智能推荐功能，包括：
 * - 智能推荐搜索
 * - 缓存管理
 */

import axios from 'axios'

const API_BASE_URL = '/api'

// ==================== 类型导入 ====================

import type {
  ScenarioType,
  MatchLevel,
  RecommendationRequest,
  LearnableElements,
  RecommendationItem,
  RecommendationResponse,
  ClearCacheRequest,
  ClearCacheResponse,
  CacheStatsResponse
} from '../types/recommendation'

// ==================== 智能推荐 API ====================

/**
 * 获取智能推荐列表
 *
 * 基于AI分析结果进行推荐，返回可复用的学习要点
 *
 * @param request - 推荐请求参数
 * @returns Promise 包含推荐结果
 */
export async function getRecommendations(
  request: RecommendationRequest
): Promise<RecommendationResponse> {
  try {
    const response = await axios.post<RecommendationResponse>(
      `${API_BASE_URL}/recommendations`,
      request,
      {
        timeout: 30000 // 30秒超时
      }
    )
    return response.data
  } catch (error: any) {
    if (axios.isAxiosError(error)) {
      if (error.code === 'ECONNABORTED') {
        return {
          success: false,
          data: {
            topic: request.topic,
            scenario: request.scenario,
            total: 0,
            results: []
          }
        }
      }
      if (!error.response) {
        return {
          success: false,
          data: {
            topic: request.topic,
            scenario: request.scenario,
            total: 0,
            results: []
          }
        }
      }
      // 处理特定错误码
      if (error.response.status === 404) {
        return {
          success: false,
          data: {
            topic: request.topic,
            scenario: request.scenario,
            total: 0,
            results: []
          }
        }
      }
      return {
        success: false,
        data: {
          topic: request.topic,
          scenario: request.scenario,
          total: 0,
          results: []
        }
      }
    }
    return {
      success: false,
      data: {
        topic: request.topic,
        scenario: request.scenario,
        total: 0,
        results: []
      }
    }
  }
}

/**
 * 清除推荐缓存
 *
 * @param request - 缓存清除请求参数
 * @returns Promise 包含清除结果
 */
export async function clearRecommendationCache(
  request: ClearCacheRequest = {}
): Promise<ClearCacheResponse> {
  try {
    const response = await axios.delete<ClearCacheResponse>(
      `${API_BASE_URL}/recommendations/cache`,
      {
        timeout: 10000, // 10秒超时
        data: request
      }
    )
    return response.data
  } catch (error: any) {
    if (axios.isAxiosError(error)) {
      if (error.code === 'ECONNABORTED') {
        return { success: false, data: { cleared_count: 0 } }
      }
      if (!error.response) {
        return { success: false, data: { cleared_count: 0 } }
      }
      const errorMessage = error.response?.data?.error || error.message || '清除缓存失败'
      console.error('清除缓存失败:', errorMessage)
      return { success: false, data: { cleared_count: 0 } }
    }
    return { success: false, data: { cleared_count: 0 } }
  }
}

/**
 * 获取缓存统计信息
 *
 * @returns Promise 包含缓存统计数据
 */
export async function getCacheStats(): Promise<CacheStatsResponse> {
  try {
    const response = await axios.get<CacheStatsResponse>(
      `${API_BASE_URL}/recommendations/cache/stats`,
      {
        timeout: 10000 // 10秒超时
      }
    )
    return response.data
  } catch (error: any) {
    if (axios.isAxiosError(error)) {
      if (error.code === 'ECONNABORTED') {
        return {
          success: false,
          data: {
            total_entries: 0,
            expired_entries: 0
          }
        }
      }
      if (!error.response) {
        return {
          success: false,
          data: {
            total_entries: 0,
            expired_entries: 0
          }
        }
      }
      const errorMessage = error.response?.data?.error || error.message || '获取缓存统计失败'
      console.error('获取缓存统计失败:', errorMessage)
      return {
        success: false,
        data: {
          total_entries: 0,
          expired_entries: 0
        }
      }
    }
    return {
      success: false,
      data: {
        total_entries: 0,
        expired_entries: 0
      }
    }
  }
}
