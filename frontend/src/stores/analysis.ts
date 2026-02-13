/**
 * 对标分析状态管理 Store
 *
 * 功能说明：
 * - 管理对标分析的笔记选择
 * - 管理分析侧边栏状态
 * - 管理分析结果（占位，后续实现）
 * - 通过后端 API 持久化存储待分析笔记列表
 */
import { defineStore } from 'pinia'
import type { ReferenceRecord } from '../api'
import type { Comment } from '@/types/analysis'

/**
 * 分析结果类型（占位，后续实现）
 */
export interface AnalysisResult {
  record_id: string
  analyzed: boolean
  content?: string // 分析内容，后续实现
  created_at?: string
}

/**
 * 数据源模式
 */
export type AnalysisDataSourceMode = 'selected' | 'all'

/**
 * 对标分析 Store 状态
 */
export interface AnalysisState {
  // 数据源模式：selected=从选中列表分析, all=从全部数据中筛选
  dataSourceMode: AnalysisDataSourceMode

  // 待分析笔记列表（从对标文案页面选中的）
  pendingRecords: ReferenceRecord[]

  // 已完成分析的笔记列表
  completedRecords: ReferenceRecord[]

  // 已总结的笔记列表
  summarizedRecords: ReferenceRecord[]

  // 当前选中的记录（用于分析）
  selectedRecord: ReferenceRecord | null

  // 分析结果缓存（按 record_id 存储）
  analysisResults: Map<string, AnalysisResult>

  // 侧边栏展开状态
  sidebarExpanded: boolean

  // 加载状态
  loading: boolean

  // 初始化状态
  initialized: boolean

  // 草稿数据缓存
  draftCache: Map<string, any>

  // 正在分析中的记录ID集合（防止重复提交）
  analyzingRecordIds: Set<string>

  // 批量选择模式是否启用
  batchSelectionEnabled: boolean

  // 批量选中的记录ID集合
  selectedRecordIds: Set<string>
}

/**
 * 分析草稿数据类型
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
  created_at?: string
  updated_at?: string
}

export const useAnalysisStore = defineStore('analysis', {
  state: (): AnalysisState => ({
    dataSourceMode: 'selected',
    pendingRecords: [],
    completedRecords: [],
    summarizedRecords: [],
    selectedRecord: null,
    analysisResults: new Map(),
    sidebarExpanded: false,
    loading: false,
    initialized: false,
    draftCache: new Map(),
    analyzingRecordIds: new Set(),
    batchSelectionEnabled: false,
    selectedRecordIds: new Set()
  }),

  getters: {
    // 当前记录的分析结果
    currentAnalysisResult(state): AnalysisResult | undefined {
      if (!state.selectedRecord) return undefined
      return state.analysisResults.get(state.selectedRecord.record_id)
    },

    // 当前记录是否已分析
    isAnalyzed(state): boolean {
      if (!state.selectedRecord) return false
      const result = state.analysisResults.get(state.selectedRecord.record_id)
      return result?.analyzed ?? false
    },

    // 待分析笔记数量
    pendingCount(state): number {
      return state.pendingRecords.length
    },

    // 是否有待分析笔记
    hasPendingRecords(state): boolean {
      return state.pendingRecords.length > 0
    },

    // 检查指定记录是否正在分析中
    isAnalyzing: (state) => (recordId: string): boolean => {
      return state.analyzingRecordIds.has(recordId)
    },

    // 检查指定记录是否已有分析结果
    hasAnalysisResult: (state) => (recordId: string): boolean => {
      const result = state.analysisResults.get(recordId)
      return result?.analyzed ?? false
    },

    // 批量选择数量
    selectedCount(state): number {
      return state.selectedRecordIds.size
    }
  },

  actions: {
    /**
     * 初始化：从后端加载待分析笔记列表
     */
    async initialize() {
      if (this.initialized) return

      try {
        // 只获取 status=pending 的记录
        const response = await fetch('/api/analysis/pending?status=pending')
        const data = await response.json()

        if (data.success) {
          this.pendingRecords = data.data || []
          this.initialized = true
        }
      } catch (e) {
        console.error('[AnalysisStore] Failed to initialize:', e)
      }
    },

    /**
     * 加载已完成分析的笔记列表
     */
    async loadCompletedRecords() {
      try {
        // 获取 status=completed 的记录
        const response = await fetch('/api/analysis/pending?status=completed')
        const data = await response.json()

        if (data.success) {
          this.completedRecords = data.data || []
        }
      } catch (e) {
        console.error('[AnalysisStore] Failed to load completed records:', e)
      }
    },

    /**
     * 加载已总结的笔记列表
     */
    async loadSummarizedRecords() {
      try {
        // 获取 status=summarized 的记录
        const response = await fetch('/api/analysis/pending?status=summarized')
        const data = await response.json()

        if (data.success) {
          this.summarizedRecords = data.data || []
        }
      } catch (e) {
        console.error('[AnalysisStore] Failed to load summarized records:', e)
      }
    },

    /**
     * 刷新待分析笔记列表（分析完成后调用）
     */
    async refreshPendingRecords() {
      try {
        const response = await fetch('/api/analysis/pending?status=pending')
        const data = await response.json()

        if (data.success) {
          this.pendingRecords = data.data || []
          console.log('[AnalysisStore] Pending records refreshed, count:', this.pendingRecords.length)
        }
      } catch (e) {
        console.error('[AnalysisStore] Failed to refresh pending records:', e)
      }
    },

    /**
     * 切换数据源模式
     */
    setDataSourceMode(mode: AnalysisDataSourceMode) {
      this.dataSourceMode = mode
    },

    /**
     * 添加笔记到待分析列表（同步到后端）
     */
    async addPendingRecord(record: ReferenceRecord) {
      // 避免重复添加
      if (this.pendingRecords.some(r => r.record_id === record.record_id)) {
        return
      }

      // 调用后端 API
      try {
        const response = await fetch('/api/analysis/pending', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ records: [record] })
        })
        const data = await response.json()

        if (data.success) {
          this.pendingRecords.push(record)
        }
      } catch (e) {
        console.error('[AnalysisStore] Failed to add pending record:', e)
      }
    },

    /**
     * 批量添加笔记到待分析列表
     */
    async addPendingRecords(records: ReferenceRecord[]) {
      if (records.length === 0) return

      // 调用后端 API
      try {
        const response = await fetch('/api/analysis/pending', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ records })
        })
        const data = await response.json()

        if (data.success) {
          // 合并到现有列表（避免重复）
          const existingIds = new Set(this.pendingRecords.map(r => r.record_id))
          for (const record of records) {
            if (!existingIds.has(record.record_id)) {
              this.pendingRecords.push(record)
              existingIds.add(record.record_id)
            }
          }
        }
      } catch (e) {
        console.error('[AnalysisStore] Failed to add pending records:', e)
      }
    },

    /**
     * 从待分析列表中移除笔记（同步到后端）
     */
    async removePendingRecord(recordId: string) {
      // 调用后端 API
      try {
        const response = await fetch(`/api/analysis/pending/${recordId}`, {
          method: 'DELETE'
        })
        const data = await response.json()

        if (data.success) {
          const index = this.pendingRecords.findIndex(r => r.record_id === recordId)
          if (index !== -1) {
            this.pendingRecords.splice(index, 1)
          }
        }
      } catch (e) {
        console.error('[AnalysisStore] Failed to remove pending record:', e)
      }
    },

    /**
     * 清空待分析列表（同步到后端）
     */
    async clearPendingRecords() {
      // 调用后端 API
      try {
        const response = await fetch('/api/analysis/pending', {
          method: 'DELETE'
        })
        const data = await response.json()

        if (data.success) {
          this.pendingRecords = []
        }
      } catch (e) {
        console.error('[AnalysisStore] Failed to clear pending records:', e)
      }
    },

    /**
     * 检查笔记是否在待分析列表中
     */
    isPending(recordId: string): boolean {
      return this.pendingRecords.some(r => r.record_id === recordId)
    },

    /**
     * 选择记录进行分析（同时加载该记录的分析结果）
     */
    async selectRecord(record: ReferenceRecord | null) {
      this.selectedRecord = record
      if (record) {
        this.sidebarExpanded = true
        // 加载该记录的分析结果（如果尚未加载）
        if (!this.analysisResults.has(record.record_id)) {
          await this.loadAnalysisResult(record.record_id)
        }
      }
    },

    /**
     * 加载指定记录的分析结果
     */
    async loadAnalysisResult(recordId: string): Promise<void> {
      try {
        const response = await fetch(`/api/analysis/result/${recordId}`)
        const data = await response.json()

        if (data.success && data.data) {
          this.setAnalysisResult(recordId, {
            record_id: recordId,
            analyzed: data.data.analyzed,
            content: data.data.content,
            created_at: data.data.created_at
          })
        }
      } catch (e) {
        console.error('[AnalysisStore] Failed to load analysis result:', e)
      }
    },

    /**
     * 加载所有分析结果
     */
    async loadAllAnalysisResults(): Promise<void> {
      try {
        const response = await fetch('/api/analysis/results')
        const data = await response.json()

        if (data.success && data.data) {
          // data.data is an object with record_id as keys
          // Use Object.values() to get the array of results
          const results = Object.values(data.data) as Array<{
            record_id: string
            analyzed: boolean
            content?: string
            created_at: string
          }>
          for (const result of results) {
            this.setAnalysisResult(result.record_id, {
              record_id: result.record_id,
              analyzed: result.analyzed,
              content: result.content,
              created_at: result.created_at
            })
          }
        }
      } catch (e) {
        console.error('[AnalysisStore] Failed to load all analysis results:', e)
      }
    },

    /**
     * 切换侧边栏
     */
    toggleSidebar() {
      this.sidebarExpanded = !this.sidebarExpanded
    },

    /**
     * 关闭侧边栏
     */
    closeSidebar() {
      this.sidebarExpanded = false
    },

    /**
     * 设置分析结果（占位，后续实现）
     */
    setAnalysisResult(recordId: string, result: AnalysisResult) {
      this.analysisResults.set(recordId, result)
    },

    /**
     * 清除当前选择
     */
    clearSelection() {
      this.selectedRecord = null
    },

    // ==================== Draft Management ====================

    /**
     * 获取指定记录的草稿数据
     */
    async getDraft(recordId: string): Promise<AnalysisDraft | null> {
      try {
        const response = await fetch(`/api/analysis/draft?record_id=${recordId}`)
        const data = await response.json()

        if (data.success && data.data) {
          this.draftCache.set(recordId, data.data)
          return data.data
        }
        return null
      } catch (e) {
        console.error('[AnalysisStore] Failed to get draft:', e)
        return null
      }
    },

    /**
     * 保存草稿
     */
    async saveDraft(draftData: Partial<AnalysisDraft>): Promise<boolean> {
      try {
        const response = await fetch('/api/analysis/draft', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(draftData)
        })
        const data = await response.json()

        if (data.success) {
          this.draftCache.set(draftData.record_id!, data.data)
          return true
        }
        return false
      } catch (e) {
        console.error('[AnalysisStore] Failed to save draft:', e)
        return false
      }
    },

    /**
     * 提交分析（使用 SSE 流式）
     */
    async submitAnalysis(
      draftData: Partial<AnalysisDraft>,
      onStep?: (step: string) => void
    ): Promise<boolean> {
      const recordId = draftData.record_id!

      // 检查是否正在分析中
      if (this.analyzingRecordIds.has(recordId)) {
        console.warn('[AnalysisStore] Record already analyzing:', recordId)
        return false
      }

      // 标记为正在分析
      this.analyzingRecordIds.add(recordId)

      try {
        this.loading = true

        // Import SSE function
        const { analyzeStream } = await import('@/api/analysis')

        await analyzeStream(
          recordId,
          draftData,
          {
            // onProgress
            onProgress: (data) => {
              console.log('[AnalysisStore] Analysis progress:', data.message)
              // 通知调用者进度步骤
              if (onStep && data.step) {
                onStep(data.step)
              }
            },
            // onComplete
            onComplete: async (data) => {
              console.log('[AnalysisStore] Analysis complete:', data.record_id)
              this.setAnalysisResult(data.record_id, {
                record_id: data.record_id,
                analyzed: true,
                content: data.content,
                created_at: new Date().toISOString()
              })
              // 刷新待分析列表（移除已完成的笔记）
              await this.refreshPendingRecords()
              // 刷新已完成记录列表（在分析结果标签页显示）
              await this.loadCompletedRecords()
              if (onStep) {
                onStep('保存完成')
              }
            },
            // onError
            onError: (data) => {
              console.error('[AnalysisStore] Analysis error:', data.error)
              this.setAnalysisResult(data.record_id, {
                record_id: data.record_id,
                analyzed: false,
                content: `Error: ${data.error}`,
                created_at: new Date().toISOString()
              })
              if (onStep) {
                onStep('分析失败')
              }
            },
            // onFinish
            onFinish: (data) => {
              console.log('[AnalysisStore] Analysis finished:', data.record_id)
              // 移除正在分析标记
              this.analyzingRecordIds.delete(recordId)
              this.loading = false
              if (onStep) {
                onStep('')
              }
            },
            // onStreamError
            onStreamError: (error) => {
              console.error('[AnalysisStore] Stream error:', error)
              // 移除正在分析标记
              this.analyzingRecordIds.delete(recordId)
              this.loading = false
              if (onStep) {
                onStep('连接失败')
              }
            }
          }
        )

        return true
      } catch (e) {
        console.error('[AnalysisStore] Failed to submit analysis:', e)
        // 移除正在分析标记
        this.analyzingRecordIds.delete(recordId)
        this.loading = false
        return false
      }
    },

    /**
     * 生成视觉描述
     */
    async generateVisualDescription(recordId: string, imageIndices: number[]): Promise<string | null> {
      try {
        const response = await fetch('/api/analysis/visual-desc', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            record_id: recordId,
            image_indices: imageIndices
          })
        })
        const data = await response.json()

        if (data.success && data.data?.description) {
          return data.data.description
        }
        return null
      } catch (e) {
        console.error('[AnalysisStore] Failed to generate visual description:', e)
        return null
      }
    },

    // ==================== Batch Selection ====================

    /**
     * 切换批量选择模式
     */
    toggleBatchSelection() {
      this.batchSelectionEnabled = !this.batchSelectionEnabled
      // 退出批量模式时清空选择
      if (!this.batchSelectionEnabled) {
        this.selectedRecordIds.clear()
      }
    },

    /**
     * 启用批量选择模式
     */
    enableBatchSelection() {
      this.batchSelectionEnabled = true
    },

    /**
     * 禁用批量选择模式
     */
    disableBatchSelection() {
      this.batchSelectionEnabled = false
      this.selectedRecordIds.clear()
    },

    /**
     * 切换单个记录的选择状态
     */
    toggleRecordSelection(recordId: string) {
      if (this.selectedRecordIds.has(recordId)) {
        this.selectedRecordIds.delete(recordId)
      } else {
        this.selectedRecordIds.add(recordId)
      }
    },

    /**
     * 选择记录（批量模式）
     */
    selectRecordForBatch(recordId: string) {
      this.selectedRecordIds.add(recordId)
    },

    /**
     * 取消选择记录（批量模式）
     */
    deselectRecordForBatch(recordId: string) {
      this.selectedRecordIds.delete(recordId)
    },

    /**
     * 清空批量选择
     */
    clearBatchSelection() {
      this.selectedRecordIds.clear()
    },

    /**
     * 全选当前列表
     */
    selectAll(records: ReferenceRecord[]) {
      this.selectedRecordIds.clear()
      for (const record of records) {
        this.selectedRecordIds.add(record.record_id)
      }
    },

    /**
     * 检查记录是否被选中
     */
    isRecordSelected(recordId: string): boolean {
      return this.selectedRecordIds.has(recordId)
    },

    /**
     * 按行业分组选择
     */
    getRecordsByIndustry(): Map<string, ReferenceRecord[]> {
      const grouped = new Map<string, ReferenceRecord[]>()
      for (const record of this.completedRecords) {
        const industry = record.industry || '未分类'
        if (!grouped.has(industry)) {
          grouped.set(industry, [])
        }
        grouped.get(industry)!.push(record)
      }
      return grouped
    }
  }
})
