<template>
  <div class="analysis-view">
    <!-- 顶部导航栏 -->
    <header class="top-header">
      <div class="header-left">
        <h1 class="page-title">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2"></path>
            <rect x="9" y="3" width="6" height="4" rx="1"></rect>
            <path d="M9 14l2 2 4-4"></path>
          </svg>
          对标分析
        </h1>
      </div>
      <div class="header-actions">
        <!-- 每页条数 -->
        <select :value="pageSize" @change="handlePageSizeChange" class="page-size-select">
          <option :value="20">20 条/页</option>
          <option :value="50">50 条/页</option>
          <option :value="100">100 条/页</option>
        </select>
      </div>
    </header>

    <!-- 主内容区：左侧侧边栏 + 右侧内容 -->
    <div class="main-container" :class="{ 'with-sidebar': analysisStore.sidebarExpanded }">
      <!-- 左侧固定面板 -->
      <aside class="sidebar">
        <!-- 快捷筛选 -->
        <div class="sidebar-section filters-section">
          <h3 class="section-title">筛选条件</h3>
          <div class="filter-group">
            <input
              v-model="filters.keyword"
              type="text"
              placeholder="搜索关键词..."
              class="filter-input"
              @keyup.enter="handleSearch"
            />
            <select
              v-model="filters.industry"
              class="filter-select"
              @change="handleSearch"
            >
              <option value="">所有行业</option>
              <option v-for="industry in availableIndustries" :key="industry" :value="industry">
                {{ industry }}
              </option>
            </select>
            <select
              v-model="filters.note_type"
              class="filter-select"
              @change="handleSearch"
            >
              <option value="">所有类型</option>
              <option value="图文">图文</option>
              <option value="视频">视频</option>
            </select>
          </div>
        </div>

        <!-- 统计信息 -->
        <div class="sidebar-section stats-section">
          <h3 class="section-title">数据统计</h3>
          <div class="stats-list">
            <div class="stat-item">
              <span class="stat-label">总记录数</span>
              <span class="stat-value">{{ totalRecords }}</span>
            </div>
          </div>
        </div>
      </aside>

      <!-- 右侧内容区 -->
      <main class="content-area">
        <!-- 数据源提示 -->
        <div class="data-source-bar">
          <div class="source-info">
            已选笔记 ({{ analysisStore.pendingCount }})
          </div>

          <!-- 排序选项 -->
          <div class="sort-bar">
            <span class="sort-label">排序：</span>
            <select :value="sortBy" @change="handleSortByChange" class="sort-select">
              <option value="created_at">最新发布</option>
              <option value="likes">点赞最多</option>
              <option value="saves">收藏最多</option>
              <option value="comments">评论最多</option>
              <option value="total_engagement">总互动量</option>
              <option value="save_ratio">收藏比</option>
            </select>
            <button
              class="sort-order"
              :class="{ desc: sortOrder === 'desc' }"
              @click="toggleSortOrder"
              :title="sortOrder === 'desc' ? '降序' : '升序'"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="12" y1="5" x2="12" y2="19"></line>
                <polyline points="19 12 12 19 5 12"></polyline>
              </svg>
            </button>
          </div>
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
              </svg>
            </div>
            <h3>{{ hasActiveFilters ? '没有符合条件的记录' : '暂无数据' }}</h3>
            <p>{{ hasActiveFilters ? '试试调整筛选条件' : '请先在对标文案页面同步数据' }}</p>
          </div>

          <!-- 卡片网格 -->
          <div v-else class="records-grid">
            <AnalysisCard
              v-for="record in paginatedRecords"
              :key="record.record_id"
              :record="record"
              @analyze="handleAnalyze"
              @detail="handleDetail"
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
      </main>
    </div>

    <!-- 分析侧边栏 -->
    <AnalysisSidebar />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useReferenceStore } from '@/stores/reference'
import { useAnalysisStore } from '@/stores/analysis'
import AnalysisCard from '@/components/analysis/AnalysisCard.vue'
import AnalysisSidebar from '@/components/analysis/AnalysisSidebar.vue'

/**
 * 对标分析页面
 *
 * 与对标文案页面类似，但每条笔记都有"对标分析"按钮
 */

const referenceStore = useReferenceStore()
const analysisStore = useAnalysisStore()

// 筛选条件
const filters = ref({
  keyword: '',
  industry: '',
  note_type: ''
})

// 分页
const currentPage = ref(1)
const pageSize = ref(20)

// 排序
const sortBy = ref<'created_at' | 'likes' | 'saves' | 'comments' | 'total_engagement' | 'save_ratio'>('created_at')
const sortOrder = ref<'asc' | 'desc'>('desc')

// 加载状态
const loading = ref(false)

// 可用行业列表
const availableIndustries = computed(() => {
  if (!referenceStore.stats) return []
  return Object.keys(referenceStore.stats.industry_distribution)
})

// 总记录数（已选笔记数量）
const totalRecords = computed(() => {
  return analysisStore.pendingRecords.length
})

// 基础数据源（已选笔记）
const baseRecords = computed(() => {
  return analysisStore.pendingRecords
})

// 筛选后的记录
const filteredRecords = computed(() => {
  let records = [...baseRecords.value]

  if (filters.value.keyword) {
    const keyword = filters.value.keyword.toLowerCase()
    records = records.filter(r =>
      r.title.toLowerCase().includes(keyword) ||
      r.body?.toLowerCase().includes(keyword)
    )
  }

  if (filters.value.industry) {
    records = records.filter(r => r.industry === filters.value.industry)
  }

  if (filters.value.note_type) {
    records = records.filter(r => r.note_type === filters.value.note_type)
  }

  // 排序
  records.sort((a, b) => {
    // 获取排序值（指标字段在 metrics 对象下）
    let aValue: number | string | null | undefined
    let bValue: number | string | null | undefined

    if (sortBy.value === 'created_at') {
      aValue = a[sortBy.value]
      bValue = b[sortBy.value]
    } else {
      // metrics 相关字段
      aValue = a.metrics?.[sortBy.value as keyof typeof a.metrics]
      bValue = b.metrics?.[sortBy.value as keyof typeof b.metrics]
    }

    // 处理 null/undefined
    if (aValue == null) return 1
    if (bValue == null) return -1

    if (typeof aValue === 'number' && typeof bValue === 'number') {
      return sortOrder.value === 'desc' ? bValue - aValue : aValue - bValue
    }

    // 字符串比较
    const aStr = String(aValue)
    const bStr = String(bValue)
    const comparison = aStr.localeCompare(bStr)
    return sortOrder.value === 'desc' ? -comparison : comparison
  })

  return records
})

// 分页后的记录
const paginatedRecords = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredRecords.value.slice(start, end)
})

// 总页数
const totalPages = computed(() => {
  return Math.ceil(filteredRecords.value.length / pageSize.value)
})

// 是否有筛选条件
const hasActiveFilters = computed(() => {
  return !!(filters.value.keyword || filters.value.industry || filters.value.note_type)
})

// 初始化
onMounted(async () => {
  loading.value = true
  try {
    // 初始化分析 store（从后端加载已选笔记）
    await analysisStore.initialize()

    // 如果 reference store 没有数据，先获取
    if (referenceStore.records.length === 0) {
      await referenceStore.fetchRecords()
    }
    // 获取统计信息
    if (!referenceStore.stats) {
      await referenceStore.fetchStats()
    }
  } finally {
    loading.value = false
  }
})

// 搜索
function handleSearch() {
  currentPage.value = 1
}

// 排序字段切换
function handleSortByChange(event: Event) {
  sortBy.value = (event.target as HTMLSelectElement).value as typeof sortBy.value
}

// 切换排序顺序
function toggleSortOrder() {
  sortOrder.value = sortOrder.value === 'desc' ? 'asc' : 'desc'
}

// 清除单个筛选条件
function clearFilter(key: keyof typeof filters.value) {
  filters.value[key] = ''
  handleSearch()
}

// 清除所有筛选条件
function clearAllFilters() {
  filters.value = {
    keyword: '',
    industry: '',
    note_type: ''
  }
  handleSearch()
}

// 修改每页条数
function handlePageSizeChange(event: Event) {
  pageSize.value = Number((event.target as HTMLSelectElement).value)
  currentPage.value = 1
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

// 对标分析
function handleAnalyze(recordId: string) {
  const record = referenceStore.records.find(r => r.record_id === recordId)
  if (record) {
    analysisStore.selectRecord(record)
  }
}

// 查看详情（可选功能）
function handleDetail(recordId: string) {
  console.log('查看详情:', recordId)
  // 可以打开详情弹窗或跳转页面
}
</script>

<style scoped>
/* 页面容器 */
.analysis-view {
  min-height: 100vh;
  background: #f8f7f5;
  display: flex;
  flex-direction: column;
}

/* 顶部导航栏 */
.top-header {
  position: sticky;
  top: 0;
  z-index: 100;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 32px;
  height: 64px;
  background: white;
  border-bottom: 1px solid #e8e6e3;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 24px;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 20px;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0;
}

.page-title svg {
  color: var(--primary, #ff2442);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* 每页条数选择 */
.page-size-select {
  padding: 8px 32px 8px 14px;
  border: 1px solid #e0dedb;
  border-radius: 8px;
  background: white;
  font-size: 13px;
  font-weight: 500;
  color: #1a1a1a;
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%23666' stroke-width='2.5'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 10px center;
  transition: border-color 0.2s;
}

.page-size-select:hover {
  border-color: #ccc;
}

/* 主容器 */
.main-container {
  display: flex;
  flex: 1;
  gap: 0;
  overflow: hidden;
  transition: padding-right 0.3s ease;
}

.main-container.with-sidebar {
  padding-right: 400px;
}

/* 左侧边栏 */
.sidebar {
  width: 280px;
  flex-shrink: 0;
  padding: 24px 24px 24px 32px;
  overflow-y: auto;
  border-right: 1px solid #e8e6e3;
  background: white;
}

.sidebar-section {
  margin-bottom: 24px;
}

.section-title {
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: #999;
  margin: 0 0 16px 0;
}

/* 筛选输入 */
.filter-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.filter-input,
.filter-select {
  padding: 10px 14px;
  border: 1px solid #e0dedb;
  border-radius: 8px;
  background: white;
  font-size: 13px;
  color: #1a1a1a;
  transition: border-color 0.2s;
}

.filter-input:focus,
.filter-select:focus {
  outline: none;
  border-color: var(--primary, #ff2442);
}

.filter-input::placeholder {
  color: #999;
}

/* 统计信息 */
.stats-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  padding: 12px 16px;
  background: #f8f7f5;
  border-radius: 8px;
}

.stat-label {
  font-size: 13px;
  color: #666;
}

.stat-value {
  font-size: 16px;
  font-weight: 700;
  color: #1a1a1a;
}

/* 右侧内容区 */
.content-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 24px 32px;
  overflow: hidden;
}

/* 数据源提示栏 */
.data-source-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
  padding: 12px 16px;
  background: linear-gradient(135deg, rgba(255, 36, 66, 0.08) 0%, rgba(255, 107, 107, 0.08) 100%);
  border-radius: 10px;
  border: 1px solid rgba(255, 36, 66, 0.15);
}

.source-info {
  font-size: 14px;
  font-weight: 600;
  color: var(--primary, #ff2442);
}

/* 排序栏 */
.sort-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: auto;
}

.sort-label {
  font-size: 13px;
  color: #666;
  font-weight: 500;
}

.sort-select {
  padding: 8px 32px 8px 14px;
  border: 1px solid #e0dedb;
  border-radius: 8px;
  background: white;
  font-size: 13px;
  font-weight: 500;
  color: #1a1a1a;
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%23666' stroke-width='2.5'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 10px center;
}

.sort-order {
  width: 32px;
  height: 32px;
  padding: 0;
  border: 1px solid #e0dedb;
  background: white;
  border-radius: 6px;
  color: #666;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.sort-order:hover {
  border-color: var(--primary, #ff2442);
  color: var(--primary, #ff2442);
}

.sort-order.desc svg {
  transform: rotate(180deg);
}

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
</style>
