/**
 * AI总结状态管理 Store
 *
 * 功能说明：
 * - 管理AI总结的加载和状态
 * - 管理总结生成流程（SSE流式）
 * - 按行业分组显示总结结果
 */
import { defineStore } from 'pinia'

/**
 * 总结数据类型
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
 * 生成进度类型
 */
export interface SummaryProgress {
  step: string
  message: string
}

/**
 * AI总结 Store 状态
 */
export interface SummaryState {
  // 所有总结列表（按时间倒序）
  summaries: Summary[]

  // 按行业分组的总结
  summariesByIndustry: Map<string, Summary[]>

  // 行业列表
  industries: string[]

  // 当前选中的行业过滤
  selectedIndustry: string | null

  // 加载状态
  loading: boolean

  // 生成中的行业集合（防止重复生成）
  generatingIndustries: Set<string>

  // 错误信息
  error: string | null
}

export const useSummaryStore = defineStore('summary', {
  state: (): SummaryState => ({
    summaries: [],
    summariesByIndustry: new Map(),
    industries: [],
    selectedIndustry: null,
    loading: false,
    generatingIndustries: new Set(),
    error: null
  }),

  getters: {
    // 过滤后的总结列表
    filteredSummaries(state): Summary[] {
      if (!state.selectedIndustry) {
        return state.summaries
      }
      return state.summaries.filter(s => s.industry === state.selectedIndustry)
    },

    // 检查指定行业是否正在生成
    isGenerating: (state) => (industry: string): boolean => {
      return state.generatingIndustries.has(industry)
    },

    // 按行业分组显示的总结
    groupedSummaries(state): Map<string, Summary[]> {
      const grouped = new Map<string, Summary[]>()
      for (const summary of state.summaries) {
        const industry = summary.industry
        if (!grouped.has(industry)) {
          grouped.set(industry, [])
        }
        grouped.get(industry)!.push(summary)
      }
      return grouped
    }
  },

  actions: {
    /**
     * 初始化：加载所有总结
     */
    async initialize() {
      await this.loadSummaries()
    },

    /**
     * 加载所有总结
     */
    async loadSummaries() {
      this.loading = true
      this.error = null

      try {
        const response = await fetch('/api/summary')
        const data = await response.json()

        if (data.success) {
          this.summaries = data.data || []
          this._updateIndustries()
          this._updateGroupedSummaries()
        } else {
          this.error = data.error || '加载总结失败'
        }
      } catch (e) {
        console.error('[SummaryStore] Failed to load summaries:', e)
        this.error = '加载总结失败'
      } finally {
        this.loading = false
      }
    },

    /**
     * 加载指定行业的总结
     */
    async loadSummariesByIndustry(industry: string) {
      this.loading = true
      this.error = null

      try {
        const response = await fetch(`/api/summary?industry=${encodeURIComponent(industry)}`)
        const data = await response.json()

        if (data.success) {
          // 更新该行业的总结（合并到现有列表）
          const existingIds = new Set(this.summaries.filter(s => s.industry === industry).map(s => s.id))
          for (const summary of data.data || []) {
            if (!existingIds.has(summary.id)) {
              this.summaries.push(summary)
            }
          }
          this._updateIndustries()
          this._updateGroupedSummaries()
        } else {
          this.error = data.error || '加载总结失败'
        }
      } catch (e) {
        console.error('[SummaryStore] Failed to load summaries by industry:', e)
        this.error = '加载总结失败'
      } finally {
        this.loading = false
      }
    },

    /**
     * 加载行业列表
     */
    async loadIndustries() {
      try {
        const response = await fetch('/api/summary/industries')
        const data = await response.json()

        if (data.success) {
          this.industries = data.data || []
        }
      } catch (e) {
        console.error('[SummaryStore] Failed to load industries:', e)
      }
    },

    /**
     * 获取单个总结详情
     */
    async getSummary(summaryId: number): Promise<Summary | null> {
      try {
        const response = await fetch(`/api/summary/${summaryId}`)
        const data = await response.json()

        if (data.success && data.data) {
          return data.data
        }
        return null
      } catch (e) {
        console.error('[SummaryStore] Failed to get summary:', e)
        return null
      }
    },

    /**
     * 生成 AI 总结（SSE流式）
     */
    async generateSummary(
      industry: string,
      recordIds: string[],
      onProgress?: (progress: SummaryProgress) => void
    ): Promise<boolean> {
      // 检查是否正在生成
      if (this.generatingIndustries.has(industry)) {
        console.warn('[SummaryStore] Already generating for industry:', industry)
        return false
      }

      // 标记为正在生成
      this.generatingIndustries.add(industry)
      this.error = null

      try {
        const response = await fetch('/api/summary/generate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            industry,
            record_ids: recordIds
          })
        })

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`)
        }

        const reader = response.body?.getReader()
        if (!reader) {
          throw new Error('No response body')
        }

        const decoder = new TextDecoder()
        let buffer = ''

        while (true) {
          const { done, value } = await reader.read()
          if (done) break

          buffer += decoder.decode(value, { stream: true })

          // 处理 SSE 事件
          const lines = buffer.split('\n\n')
          buffer = lines.pop() || ''

          for (const line of lines) {
            if (!line.trim()) continue

            const eventMatch = line.match(/^event: (\w+)$/)
            const dataMatch = line.match(/^data: (.+)$/)

            if (eventMatch && dataMatch) {
              const event = eventMatch[1]
              const data = JSON.parse(dataMatch[1])

              if (event === 'progress') {
                console.log('[SummaryStore] Progress:', data.message)
                if (onProgress) {
                  onProgress(data)
                }
              } else if (event === 'complete') {
                console.log('[SummaryStore] Generation complete:', data.id)
                // 重新加载总结列表
                await this.loadSummaries()
                if (onProgress) {
                  onProgress({ step: 'complete', message: '生成完成' })
                }
              } else if (event === 'error') {
                console.error('[SummaryStore] Generation error:', data.error)
                this.error = data.error
                if (onProgress) {
                  onProgress({ step: 'error', message: data.error })
                }
              } else if (event === 'finish') {
                console.log('[SummaryStore] Generation finished')
              }
            }
          }
        }

        return true
      } catch (e) {
        console.error('[SummaryStore] Failed to generate summary:', e)
        this.error = String(e)
        return false
      } finally {
        // 移除生成标记
        this.generatingIndustries.delete(industry)
      }
    },

    /**
     * 删除总结
     */
    async deleteSummary(summaryId: number): Promise<boolean> {
      try {
        const response = await fetch(`/api/summary/${summaryId}`, {
          method: 'DELETE'
        })
        const data = await response.json()

        if (data.success) {
          // 从列表中移除
          const index = this.summaries.findIndex(s => s.id === summaryId)
          if (index !== -1) {
            this.summaries.splice(index, 1)
          }
          this._updateIndustries()
          this._updateGroupedSummaries()
          return true
        }
        return false
      } catch (e) {
        console.error('[SummaryStore] Failed to delete summary:', e)
        return false
      }
    },

    /**
     * 设置行业过滤
     */
    setSelectedIndustry(industry: string | null) {
      this.selectedIndustry = industry
    },

    /**
     * 清除错误
     */
    clearError() {
      this.error = null
    },

    /**
     * 更新行业列表
     */
    _updateIndustries() {
      const industrySet = new Set<string>()
      for (const summary of this.summaries) {
        industrySet.add(summary.industry)
      }
      this.industries = Array.from(industrySet).sort()
    },

    /**
     * 更新按行业分组的总结
     */
    _updateGroupedSummaries() {
      const grouped = new Map<string, Summary[]>()
      for (const summary of this.summaries) {
        const industry = summary.industry
        if (!grouped.has(industry)) {
          grouped.set(industry, [])
        }
        grouped.get(industry)!.push(summary)
      }
      this.summariesByIndustry = grouped
    }
  }
})
