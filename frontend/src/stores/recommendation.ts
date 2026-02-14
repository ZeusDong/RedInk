// frontend/src/stores/recommendation.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

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

export interface RecommendationItem {
  record: ReferenceRecord
  match_score: number
  reasons?: string[]
}

export interface RecommendationState {
  recommendations: RecommendationItem[]
  loading: boolean
  searchTopic: string
  industries: string[]
}

export const useRecommendationStore = defineStore('recommendation', () => {
  // State
  const recommendations = ref<RecommendationItem[]>([])
  const loading = ref(false)
  const searchTopic = ref('')
  const industries = ref<string[]>([])

  // Getters
  const hasRecommendations = computed(() => recommendations.value.length > 0)
  const recommendationsCount = computed(() => recommendations.value.length)

  // Actions
  async function fetchRecommendations(topic: string, options?: {
    industry?: string
    scenario?: string
    limit?: number
  }) {
    loading.value = true
    searchTopic.value = topic

    try {
      const response = await fetch('/api/recommend', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          topic,
          industry: options?.industry,
          scenario: options?.scenario,
          limit: options?.limit || 20
        })
      })

      const data = await response.json()
      if (data.success) {
        recommendations.value = data.data || []
      } else {
        console.error('获取推荐失败:', data.error)
        recommendations.value = []
      }
    } catch (error) {
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
    // Getters
    hasRecommendations,
    recommendationsCount,
    // Actions
    fetchRecommendations,
    fetchIndustries,
    fetchSimilarRecommendations,
    clearRecommendations
  }
})
