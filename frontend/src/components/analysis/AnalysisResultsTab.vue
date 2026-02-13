<template>
  <div class="analysis-results-tab">
    <!-- 批量选择按钮 -->
    <div v-if="!analysisStore.batchSelectionEnabled" class="batch-actions">
      <button @click="enableBatchSelection" class="batch-enable-btn">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="3" y="3" width="18" height="18" rx="2" />
          <path d="M9 12l2 2 4-4" />
        </svg>
        批量选择
      </button>
    </div>

    <!-- 批量选择模式工具栏 -->
    <div v-if="analysisStore.batchSelectionEnabled" class="batch-toolbar">
      <div class="batch-info">
        已选 <strong>{{ analysisStore.selectedCount }}</strong> 条
      </div>
      <button @click="cancelBatchSelection" class="batch-cancel-btn">
        取消
      </button>
      <button
        v-if="analysisStore.selectedCount > 0"
        @click="generateSummary"
        class="batch-generate-btn"
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
          <path d="M12 9v3m0 0v5m-3-3h6" />
        </svg>
        生成AI总结
      </button>
    </div>

    <!-- 筛选标签 -->
    <div v-if="hasActiveFilters" class="filter-tags">
      <span class="filter-tag" v-if="filters.keyword">
        关键词: {{ filters.keyword }}
        <button @click="clearFilter('keyword')" class="tag-close">×</button>
      </span>
      <span class="filter-tag" v-if="filters.industry">
        行业: {{ filters.industry }}
        <button @click="clearFilter('industry')" class="tag-close">×</button>
      </span>
      <span class="filter-tag" v-if="filters.note_type">
        类型: {{ filters.note_type }}
        <button @click="clearFilter('note_type')" class="tag-close">×</button>
      </span>
      <button @click="clearAllFilters" class="clear-all">清空筛选</button>
    </div>

    <!-- 记录列表 -->
    <div class="records-container">
      <!-- 加载状态 -->
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>加载中...</p>
      </div>

      <!-- 空状态 -->
      <div v-else-if="filteredRecords.length === 0" class="empty-state">
        <div class="empty-icon">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2"></path>
            <rect x="9" y="3" width="6" height="4" rx="1"></rect>
            <path d="M9 14l2 2 4-4"></path>
          </svg>
        </div>
        <h3>{{ hasActiveFilters ? '没有符合条件的记录' : '暂无分析结果' }}</h3>
        <p>{{ hasActiveFilters ? '试试调整筛选条件' : '完成的分析结果会在这里显示' }}</p>
      </div>

      <!-- 卡片网格 -->
      <div v-else class="records-grid">
        <AnalysisResultCard
          v-for="record in paginatedRecords"
          :key="record.record_id"
          :record="record"
          :is-selected="analysisStore.selectedRecord?.record_id === record.record_id"
          :batch-selection-enabled="analysisStore.batchSelectionEnabled"
          :is-batch-selected="analysisStore.isRecordSelected(record.record_id)"
          @select="handleSelect"
          @toggle-select="handleToggleSelect"
        />
      </div>
    </div>

    <!-- 分页 -->
    <div v-if="totalPages > 1" class="pagination">
      <div class="pagination-info">
        <span>第 {{ currentPage }} / {{ totalPages }} 页</span>
        <span class="pagination-divider">·</span>
        <span>共 {{ filteredRecords.length }} 条</span>
      </div>
      <div class="pagination-controls">
        <button class="page-btn" :disabled="currentPage <= 1" @click="handlePrevPage">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="15 18 9 12 15 6"></polyline>
          </svg>
          上一页
        </button>
        <button class="page-btn" :disabled="currentPage >= totalPages" @click="handleNextPage">
          下一页
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="9 18 15 12 9 6"></polyline>
          </svg>
        </button>
      </div>
    </div>

    <!-- 生成总结弹窗 -->
    <GenerateSummaryModal
      v-if="showGenerateModal"
      :show="showGenerateModal"
      :records-by-industry="recordsByIndustry"
      @close="onModalClose"
      @generate="onModalGenerate"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useAnalysisStore } from '@/stores/analysis'
import { useSummaryStore } from '@/stores/summary'
import type { SummaryProgress } from '@/stores/summary'
import AnalysisResultCard from './AnalysisResultCard.vue'
import GenerateSummaryModal from '@/components/summary/GenerateSummaryModal.vue'

/**
 * 分析结果标签页组件
 *
 * 显示已分析的笔记列表，点击可在侧边栏查看分析结果
 */

const props = defineProps<{
  filters: {
    keyword: string
    industry: string
    note_type: string
  }
  sortBy: 'created_at' | 'likes' | 'saves' | 'comments' | 'total_engagement' | 'save_ratio'
  sortOrder: 'asc' | 'desc'
  pageSize: number
}>()

const emit = defineEmits<{
  (e: 'update:total', count: number): void
  (e: 'update:filters', value: { keyword: string; industry: string; note_type: string }): void
  (e: 'refresh-completed'): void
}>()

const analysisStore = useAnalysisStore()
const summaryStore = useSummaryStore()

// 分页状态
const currentPage = ref(1)
const loading = ref(false)

// Modal 状态
const showGenerateModal = ref(false)
const selectedForSummary = ref<typeof analyzedRecords.value>([])
const generateProgress = ref<{ step: string; message: string } | null>(null)

// 获取已分析的记录 - 使用 completedRecords（status=completed 的记录）
const analyzedRecords = computed(() => {
  return analysisStore.completedRecords
})

// 筛选后的记录
const filteredRecords = computed(() => {
  let records = [...analyzedRecords.value]

  if (props.filters.keyword) {
    const keyword = props.filters.keyword.toLowerCase()
    records = records.filter(r =>
      r.title.toLowerCase().includes(keyword) ||
      r.body?.toLowerCase().includes(keyword)
    )
  }

  if (props.filters.industry) {
    records = records.filter(r => r.industry === props.filters.industry)
  }

  if (props.filters.note_type) {
    records = records.filter(r => r.note_type === props.filters.note_type)
  }

  // 排序
  records.sort((a, b) => {
    let aValue: number | string | null | undefined
    let bValue: number | string | null | undefined

    if (props.sortBy === 'created_at') {
      aValue = a[props.sortBy]
      bValue = b[props.sortBy]
    } else {
      aValue = a.metrics?.[props.sortBy as keyof typeof a.metrics]
      bValue = b.metrics?.[props.sortBy as keyof typeof b.metrics]
    }

    if (aValue == null) return 1
    if (bValue == null) return -1

    if (typeof aValue === 'number' && typeof bValue === 'number') {
      return props.sortOrder === 'desc' ? bValue - aValue : aValue - bValue
    }

    const aStr = String(aValue)
    const bStr = String(bValue)
    const comparison = aStr.localeCompare(bStr)
    return props.sortOrder === 'desc' ? -comparison : comparison
  })

  return records
})

// 分页后的记录
const paginatedRecords = computed(() => {
  const start = (currentPage.value - 1) * props.pageSize
  const end = start + props.pageSize
  return filteredRecords.value.slice(start, end)
})

// 总页数
const totalPages = computed(() => {
  return Math.ceil(filteredRecords.value.length / props.pageSize)
})

// 是否有筛选条件
const hasActiveFilters = computed(() => {
  return !!(props.filters.keyword || props.filters.industry || props.filters.note_type)
})

// 按行业分组选中的记录（用于modal）
const recordsByIndustry = computed(() => {
  // 添加调试日志
  // console.log('[recordsByIndustry] recomputing, selectedForSummary.value.length:', selectedForSummary.value.length)

  const grouped = new Map<string, typeof selectedForSummary.value>()
  for (const record of selectedForSummary.value) {
    const industry = record.industry || '未分类'
    if (!grouped.has(industry)) {
      grouped.set(industry, [])
    }
    grouped.get(industry)!.push(record)
  }

  // console.log('[recordsByIndustry] result:', Array.from(grouped.entries()).map(([k, v]) => ({ industry: k, count: v.length })))
  return grouped
})

// 通知父组件更新总数
watch(() => filteredRecords.value.length, (count) => {
  emit('update:total', count)
}, { immediate: true })

// 切换页码时重置分页
watch(() => [props.filters, props.sortBy, props.sortOrder], () => {
  currentPage.value = 1
}, { deep: true })

// 选择记录
function handleSelect(recordId: string) {
  const record = analyzedRecords.value.find(r => r.record_id === recordId)
  if (record) {
    analysisStore.selectRecord(record)
  }
}

// 批量选择
function enableBatchSelection() {
  analysisStore.enableBatchSelection()
}

function cancelBatchSelection() {
  analysisStore.disableBatchSelection()
}

function handleToggleSelect(recordId: string) {
  analysisStore.toggleRecordSelection(recordId)
}

async function generateSummary() {
  const selectedRecords = analyzedRecords.value.filter(r =>
    analysisStore.isRecordSelected(r.record_id)
  )

  if (selectedRecords.length === 0) return

  selectedForSummary.value = selectedRecords

  // 调试日志
  // console.log('=== DEBUG generateSummary ===')
  // console.log('selectedRecords.length:', selectedRecords.length)
  // console.log('selectedRecords:', selectedRecords.map(r => ({
  //   id: r.record_id,
  //   title: r.title,
  //   industry: r.industry
  // })))
  // console.log('selectedForSummary.value.length:', selectedForSummary.value.length)
  // console.log('recordsByIndustry:', recordsByIndustry.value)

  showGenerateModal.value = true
}

function onModalClose() {
  showGenerateModal.value = false
  generateProgress.value = null
}

async function onModalGenerate(industries: string[]) {
  // 为每个行业生成总结
  for (const industry of industries) {
    const industryRecords = selectedForSummary.value.filter(r => r.industry === industry)
    const industryRecordIds = industryRecords.map(r => r.record_id)

    const success = await summaryStore.generateSummary(
      industry,
      industryRecordIds,
      (progress: SummaryProgress) => {
        generateProgress.value = progress
      }
    )

    if (!success) {
      console.error(`Failed to generate summary for ${industry}`)
    }
  }

  // 生成完成后
  onModalClose()
  analysisStore.disableBatchSelection()
  // 刷新已完成记录列表
  emit('refresh-completed')
}

// 清除单个筛选条件
function clearFilter(key: 'keyword' | 'industry' | 'note_type') {
  emit('update:filters', { ...props.filters, [key]: '' })
}

// 清除所有筛选条件
function clearAllFilters() {
  emit('update:filters', { keyword: '', industry: '', note_type: '' })
}

// 翻页
function handlePrevPage() {
  if (currentPage.value > 1) {
    currentPage.value--
  }
}

function handleNextPage() {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
  }
}

// 初始化加载已完成记录
onMounted(async () => {
  loading.value = true
  try {
    // completedRecords 已在父组件加载，这里只需加载分析结果内容
    await analysisStore.loadAllAnalysisResults()
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
/* 筛选标签 */
.filter-tags {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 16px;
  padding: 12px 16px;
  background: white;
  border-radius: 10px;
  border: 1px solid #e8e6e3;
}

.filter-tag {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: linear-gradient(135deg, rgba(255, 36, 66, 0.1) 0%, rgba(255, 107, 107, 0.1) 100%);
  border-radius: 6px;
  font-size: 13px;
  color: var(--primary, #ff2442);
}

.tag-close {
  border: none;
  background: transparent;
  color: var(--primary, #ff2442);
  cursor: pointer;
  font-size: 16px;
  line-height: 1;
  padding: 0;
  width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.clear-all {
  padding: 6px 12px;
  border: none;
  background: transparent;
  color: #666;
  font-size: 13px;
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.2s;
}

.clear-all:hover {
  background: #f8f7f5;
  color: #333;
}

/* 记录容器 */
.records-container {
  flex: 1;
  overflow-y: auto;
  padding-right: 8px;
}

.records-container::-webkit-scrollbar {
  width: 8px;
}

.records-container::-webkit-scrollbar-track {
  background: transparent;
}

.records-container::-webkit-scrollbar-thumb {
  background: #d0cdc9;
  border-radius: 4px;
}

.records-container::-webkit-scrollbar-thumb:hover {
  background: #b8b5b1;
}

/* 卡片网格 */
.records-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 16px;
}

/* 加载/空状态 */
.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 100px 20px;
  color: #999;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #eee;
  border-top-color: var(--primary, #ff2442);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-state .empty-icon {
  width: 64px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f0efed;
  border-radius: 50%;
  margin-bottom: 20px;
  color: #ccc;
}

.empty-state h3 {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin: 0 0 8px 0;
}

.empty-state p {
  font-size: 13px;
  color: #999;
  margin: 0;
}

/* 分页 */
.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 16px;
  border-top: 1px solid #e8e6e3;
  margin-top: 16px;
}

.pagination-info {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #666;
}

.pagination-divider {
  color: #ccc;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 12px;
}

.page-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 9px 16px;
  border-radius: 8px;
  border: 1px solid #e0dedb;
  background: white;
  color: #333;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.page-btn:hover:not(:disabled) {
  border-color: var(--primary, #ff2442);
  color: var(--primary, #ff2442);
}

.page-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

/* 批量选择样式 */
.batch-actions {
  display: flex;
  justify-content: flex-end;
  padding: 12px 16px;
  background: white;
  border-radius: 10px;
}

.batch-enable-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border: 1px solid #e0dedb;
  border-radius: 8px;
  background: white;
  color: #666;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.batch-enable-btn:hover {
  border-color: var(--primary, #ff2442);
  color: var(--primary, #ff2442);
}

.batch-enable-btn svg {
  color: #666;
}

.batch-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: linear-gradient(135deg, rgba(255, 36, 66, 0.1) 0%, rgba(255, 107, 107, 0.1) 100%);
  border-radius: 10px;
  margin-bottom: 16px;
}

.batch-info {
  font-size: 14px;
  color: var(--text-main, #1a1a1a);
}

.batch-info strong {
  color: var(--primary, #ff2442);
  font-weight: 600;
}

.batch-cancel-btn {
  padding: 8px 16px;
  border: 1px solid #e0dedb;
  border-radius: 8px;
  background: white;
  color: #666;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.batch-cancel-btn:hover {
  border-color: #ccc;
  background: #f8f8f8;
}

.batch-generate-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border: none;
  border-radius: 8px;
  background: var(--primary, #ff2442);
  color: white;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.batch-generate-btn:hover {
  background: #e61f37;
  transform: translateY(-1px);
}

.batch-generate-btn svg {
  color: white;
}
</style>
