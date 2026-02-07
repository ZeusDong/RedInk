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
}

export const useAnalysisStore = defineStore('analysis', {
  state: (): AnalysisState => ({
    dataSourceMode: 'selected',
    pendingRecords: [],
    selectedRecord: null,
    analysisResults: new Map(),
    sidebarExpanded: false,
    loading: false,
    initialized: false
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
    }
  },

  actions: {
    /**
     * 初始化：从后端加载待分析笔记列表
     */
    async initialize() {
      if (this.initialized) return

      try {
        const response = await fetch('/api/analysis/pending')
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
     * 选择记录进行分析
     */
    selectRecord(record: ReferenceRecord | null) {
      this.selectedRecord = record
      if (record) {
        this.sidebarExpanded = true
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
    }
  }
})
