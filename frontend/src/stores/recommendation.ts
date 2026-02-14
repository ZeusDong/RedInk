// frontend/src/stores/recommendation.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type {
  RecommendationItem,
  RecommendationRequest,
  ScenarioType,
  ClearCacheRequest,
  ClearCacheResponse,
  CacheStatsResponse
} from '@/types/recommendation'

/**
 * 向后兼容的接口定义
 * @deprecated 使用 RecommendationItem 代替
 */
export interface ReferenceRecord {
  record_id: string
  title: string
  cover_url: string
  images_count?: number
  industry?: string
  note_type?: string
  metrics?: {
    likes?: number
    saves?: number
    comments?: number
  }
}

/**
 * 向后兼容的接口定义
 * @deprecated 使用 RecommendationItem 代替
 */
export interface LegacyRecommendationItem {
  record: ReferenceRecord
  match_score: number
  reasons?: string[]
}

export interface RecommendationState {
  recommendations: RecommendationItem[]
  loading: boolean
  searchTopic: string
  industries: string[]
  lastSearchTime: Date | null
}

export const useRecommendationStore = defineStore('recommendation', () => {
  // State
  const recommendations = ref<RecommendationItem[]>([])
  const loading = ref(false)
  const searchTopic = ref('')
  const industries = ref<string[]>([])
  const lastSearchTime = ref<Date | null>(null)

  // Getters
  const hasRecommendations = computed(() => recommendations.value.length > 0)
  const recommendationsCount = computed(() => recommendations.value.length)

  // Actions
  /**
   * 获取智能推荐列表 (V2 API)
   */
  async function fetchRecommendations(topic: string, options?: {
    industry?: string
    scenario?: ScenarioType
    limit?: number
  }) {
    loading.value = true
    searchTopic.value = topic
    lastSearchTime.value = new Date()

    try {
      const requestBody: RecommendationRequest = {
        topic,
        limit: options?.limit || 20
      }

      if (options?.industry) requestBody.industry = options.industry
      if (options?.scenario) requestBody.scenario = options.scenario

      const response = await fetch('/api/recommendations', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody)
      })

      const data = await response.json()
      if (data.success && data.data) {
        recommendations.value = data.data.results || []
      } else {
        console.error('获取推荐失败:', data.error)
        // Handle specific error codes
        if (data.error_code === 'NO_ANALYZED_RECORDS') {
          console.warn('还没有可推荐的内容，请先进行对标分析')
        }
        recommendations.value = []
      }
    } catch (error: any) {
      console.error('获取推荐异常:', error)
      recommendations.value = []
    } finally {
      loading.value = false
    }
  }

  async function fetchIndustries() {
    try {
      const response = await fetch('/api/recommend/industries')
      const data = await response.json()
      if (data.success) {
        industries.value = data.data || []
      }
    } catch (error) {
      console.error('获取行业列表失败:', error)
    }
  }

  /**
   * 清除缓存
   */
  async function clearCache(options: ClearCacheRequest): Promise<ClearCacheResponse> {
    try {
      const response = await fetch('/api/recommendations/cache', {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(options)
      })

      const data = await response.json()
      return data
    } catch (error) {
      console.error('清除缓存失败:', error)
      return { success: false, data: { cleared_count: 0 } }
    }
  }

  /**
   * 获取缓存统计
   */
  async function getCacheStats(): Promise<CacheStatsResponse> {
    try {
      const response = await fetch('/api/recommendations/cache/stats')
      const data = await response.json()
      return data
    } catch (error) {
      console.error('获取缓存统计失败:', error)
      return {
        success: false,
        data: {
          total_entries: 0,
          expired_entries: 0
        }
      }
    }
  }

  async function fetchSimilarRecommendations(recordId: string, limit = 10) {
    try {
      const response = await fetch(`/api/recommend/similar/${recordId}?limit=${limit}`)
      const data = await response.json()
      if (data.success) {
        return data.data || []
      }
    } catch (error) {
      console.error('获取相似推荐失败:', error)
    }
    return []
  }

  function clearRecommendations() {
    recommendations.value = []
    searchTopic.value = ''
  }

  return {
    // State
    recommendations,
    loading,
    searchTopic,
    industries,
    lastSearchTime,
    // Getters
    hasRecommendations,
    recommendationsCount,
    // Actions
    fetchRecommendations,
    fetchIndustries,
    fetchSimilarRecommendations,
    clearRecommendations,
    clearCache,
    getCacheStats
  }
})
