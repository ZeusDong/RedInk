// frontend/src/stores/optimizer.ts
import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface ContentScore {
  total: number
  breakdown: {
    title: number
    structure: number
    visual: number
    engagement: number
  }
}

export interface Suggestion {
  id: string
  type: 'title' | 'structure' | 'visual' | 'engagement'
  severity: 'critical' | 'warning' | 'info' | 'success'
  message: string
  detail?: string
  action_type: 'edit' | 'insert' | 'replace' | 'reference'
  action_data?: any
  reference_record?: {
    id: string
    title: string
    url?: string
  }
  applied: boolean
}

export interface OptimizerState {
  currentContent: { title?: string; body?: string } | null
  score: ContentScore | null
  suggestions: Suggestion[]
  loading: boolean
}

export const useOptimizerStore = defineStore('optimizer', () => {
  const currentContent = ref<OptimizerState['currentContent']>(null)
  const score = ref<ContentScore | null>(null)
  const suggestions = ref<Suggestion[]>([])
  const loading = ref(false)

  async function analyzeContent(content: { title?: string; body?: string }) {
    loading.value = true
    try {
      const response = await fetch('/api/optimize/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content })
      })

      const data = await response.json()
      if (data.success) {
        currentContent.value = content
        score.value = data.data.score
        suggestions.value = data.data.suggestions || []
      }
    } catch (error) {
      console.error('分析失败:', error)
    } finally {
      loading.value = false
    }
  }

  async function applySuggestion(suggestionId: string) {
    try {
      const response = await fetch('/api/optimize/apply', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content: currentContent.value,  // 添加当前内容
          suggestion_id: suggestionId
        })
      })

      const data = await response.json()
      if (data.success) {
        const suggestion = suggestions.value.find(s => s.id === suggestionId)
        if (suggestion) {
          suggestion.applied = true
        }
        if (data.data.updated_content) {
          currentContent.value = data.data.updated_content
        }
        if (data.data.new_score) {
          score.value = data.data.new_score
        }
      }
    } catch (error) {
      console.error('应用建议失败:', error)
    }
  }

  async function dismissSuggestion(suggestionId: string) {
    try {
      const response = await fetch('/api/optimize/dismiss', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content: {
            ...currentContent.value,
            suggestions: suggestions.value
          },
          suggestion_id: suggestionId
        })
      })

      const data = await response.json()
      if (data.success) {
        const suggestion = suggestions.value.find(s => s.id === suggestionId)
        if (suggestion) {
          // 从列表中移除或标记为已忽略
          const idx = suggestions.value.indexOf(suggestion)
          suggestions.value.splice(idx, 1)
        }
      }
    } catch (error) {
      console.error('忽略建议失败:', error)
    }
  }

  function reset() {
    currentContent.value = null
    score.value = null
    suggestions.value = []
  }

  return {
    currentContent,
    score,
    suggestions,
    loading,
    analyzeContent,
    applySuggestion,
    dismissSuggestion,
    reset
  }
})
