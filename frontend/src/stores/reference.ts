/**
 * 对标文案查询状态管理 Store
 *
 * 功能说明：
 * - 管理对标文案记录的查询、筛选、排序
 * - 管理飞书配置
 * - 提供统计信息
 */
import { defineStore } from 'pinia'
import type {
  ReferenceRecord,
  ReferenceStats,
  FeishuConfig,
  ReferenceQueryParams
} from '../api'
import * as referenceApi from '../api/reference'

/**
 * 对标文案查询参数
 */
export interface ReferenceFilterState extends ReferenceQueryParams {
  keyword?: string
  industry?: string
  note_type?: string
  min_likes?: number
  min_saves?: number
  sort_by: 'created_at' | 'likes' | 'saves' | 'comments' | 'total_engagement' | 'save_ratio'
  sort_order: 'asc' | 'desc'
}

/**
 * 对标文案 Store 状态
 */
export interface ReferenceState {
  // 记录列表
  records: ReferenceRecord[]

  // 分页信息
  pagination: {
    page: number
    page_size: number
    total: number
    has_more: boolean
  }

  // 加载状态
  loading: boolean
  error: string | null

  // 当前筛选条件
  filters: ReferenceFilterState

  // 统计信息
  stats: ReferenceStats | null

  // 飞书配置
  feishuConfig: FeishuConfig | null

  // 选中的记录（用于详情查看）
  selectedRecord: ReferenceRecord | null
}

export const useReferenceStore = defineStore('reference', {
  state: (): ReferenceState => ({
    // 记录列表
    records: [],

    // 分页信息
    pagination: {
      page: 1,
      page_size: 20,
      total: 0,
      has_more: false
    },

    // 加载状态
    loading: false,
    error: null,

    // 当前筛选条件
    filters: {
      page: 1,
      page_size: 20,
      keyword: '',
      industry: '',
      note_type: '',
      min_likes: undefined,
      min_saves: undefined,
      sort_by: 'created_at',
      sort_order: 'desc'
    },

    // 统计信息
    stats: null,

    // 飞书配置
    feishuConfig: null,

    // 选中的记录
    selectedRecord: null
  }),

  getters: {
    /**
     * 获取可用的行业列表
     */
    availableIndustries(): string[] {
      if (!this.stats) return []
      return Object.keys(this.stats.industry_distribution)
    },

    /**
     * 获取可用的笔记类型列表
     */
    availableNoteTypes(): string[] {
      if (!this.stats) return []
      return Object.keys(this.stats.note_type_distribution)
    },

    /**
     * 是否有活跃的筛选条件
     */
    hasActiveFilters(): boolean {
      return !!(
        this.filters.keyword ||
        this.filters.industry ||
        this.filters.note_type ||
        this.filters.min_likes !== undefined ||
        this.filters.min_saves !== undefined
      )
    }
  },

  actions: {
    /**
     * 获取对标文案记录列表
     */
    async fetchRecords(params?: ReferenceQueryParams) {
      console.log('[Reference Store] fetchRecords called, params:', params)
      this.loading = true
      this.error = null

      try {
        // 合并筛选条件
        const queryParams: ReferenceQueryParams = {
          page: params?.page || this.filters.page,
          page_size: params?.page_size || this.filters.page_size,
          keyword: params?.keyword !== undefined ? params.keyword : this.filters.keyword,
          industry: params?.industry !== undefined ? params.industry : this.filters.industry,
          note_type: params?.note_type !== undefined ? params.note_type : this.filters.note_type,
          min_likes: params?.min_likes !== undefined ? params.min_likes : this.filters.min_likes,
          min_saves: params?.min_saves !== undefined ? params.min_saves : this.filters.min_saves,
          sort_by: params?.sort_by || this.filters.sort_by,
          sort_order: params?.sort_order || this.filters.sort_order
        }

        console.log('[Reference Store] Fetching records with params:', queryParams)
        const result = await referenceApi.getReferenceRecords(queryParams)
        console.log('[Reference Store] API result:', result)

        if (result.success) {
          console.log('[Reference Store] Records loaded:', result.records.length, result.records)
          this.records = result.records
          this.pagination = {
            page: result.page,
            page_size: result.page_size,
            total: result.total,
            has_more: result.has_more
          }

          // 更新筛选条件
          this.filters = {
            ...this.filters,
            page: result.page,
            page_size: result.page_size
          }
        } else {
          console.error('[Reference Store] API error:', result.error)
          this.error = result.error || '获取记录列表失败'
        }
      } catch (e: any) {
        console.error('[Reference Store] Fetch error:', e)
        this.error = e.message || '获取记录列表失败'
      } finally {
        this.loading = false
        console.log('[Reference Store] Loading state:', this.loading, 'Records:', this.records.length)
      }
    },

    /**
     * 获取单条记录详情
     */
    async fetchRecord(recordId: string) {
      this.loading = true
      this.error = null

      try {
        const result = await referenceApi.getReferenceRecord(recordId)

        if (result.success && result.record) {
          this.selectedRecord = result.record
          return result.record
        } else {
          this.error = result.error || '获取记录详情失败'
          return null
        }
      } catch (e: any) {
        this.error = e.message || '获取记录详情失败'
        return null
      } finally {
        this.loading = false
      }
    },

    /**
     * 获取统计信息
     */
    async fetchStats() {
      this.error = null

      try {
        console.log('[Reference Store] Fetching stats...')
        const result = await referenceApi.getReferenceStats()
        console.log('[Reference Store] Stats result:', result)

        if (result.success) {
          this.stats = result
        } else {
          console.error('[Reference Store] Stats error:', result.error)
          this.error = result.error || '获取统计信息失败'
        }
      } catch (e: any) {
        console.error('[Reference Store] Stats fetch error:', e)
        this.error = e.message || '获取统计信息失败'
      }
    },

    /**
     * 同步飞书数据
     */
    async syncData() {
      this.loading = true
      this.error = null

      try {
        const result = await referenceApi.syncReferenceData()

        if (result.success) {
          // 同步成功后重新获取记录列表
          await this.fetchRecords()
          await this.fetchStats()
          return result
        } else {
          this.error = result.error || '同步数据失败'
          return null
        }
      } catch (e: any) {
        this.error = e.message || '同步数据失败'
        return null
      } finally {
        this.loading = false
      }
    },

    /**
     * 获取飞书配置
     */
    async fetchFeishuConfig() {
      this.error = null

      try {
        const result = await referenceApi.getFeishuConfig()

        if (result.success && result.config) {
          this.feishuConfig = result.config
          return result.config
        } else {
          this.error = result.error || '获取飞书配置失败'
          return null
        }
      } catch (e: any) {
        this.error = e.message || '获取飞书配置失败'
        return null
      }
    },

    /**
     * 更新飞书配置
     */
    async updateFeishuConfig(config: FeishuConfig) {
      this.loading = true
      this.error = null

      try {
        const result = await referenceApi.updateFeishuConfig(config)

        if (result.success) {
          this.feishuConfig = config
          return true
        } else {
          this.error = result.error || '更新飞书配置失败'
          return false
        }
      } catch (e: any) {
        this.error = e.message || '更新飞书配置失败'
        return false
      } finally {
        this.loading = false
      }
    },

    /**
     * 测试飞书连接
     */
    async testConnection(config: {
      app_id: string
      app_secret: string
      user_access_token?: string
      base_url: string
    }) {
      this.error = null

      try {
        const result = await referenceApi.testFeishuConnection(config)
        return result
      } catch (e: any) {
        this.error = e.message || '测试连接失败'
        return { success: false, error: e.message }
      }
    },

    /**
     * 设置筛选条件
     */
    setFilters(filters: Partial<ReferenceFilterState>) {
      this.filters = {
        ...this.filters,
        ...filters
      }
    },

    /**
     * 重置筛选条件
     */
    resetFilters() {
      this.filters = {
        page: 1,
        page_size: 20,
        keyword: '',
        industry: '',
        note_type: '',
        min_likes: undefined,
        min_saves: undefined,
        sort_by: 'created_at',
        sort_order: 'desc'
      }
    },

    /**
     * 设置排序
     */
    setSort(sortBy: ReferenceFilterState['sort_by'], sortOrder: ReferenceFilterState['sort_order'] = 'desc') {
      this.filters.sort_by = sortBy
      this.filters.sort_order = sortOrder
    },

    /**
     * 跳转到指定页
     */
    goToPage(page: number) {
      this.filters.page = page
    },

    /**
     * 清除错误
     */
    clearError() {
      this.error = null
    },

    /**
     * 设置每页条数
     */
    setPageSize(pageSize: number) {
      this.filters.page_size = pageSize
      this.filters.page = 1 // 重置到第一页
    },

    /**
     * 清除选中的记录
     */
    clearSelectedRecord() {
      this.selectedRecord = null
    }
  }
})
