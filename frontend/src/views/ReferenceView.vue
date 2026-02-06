<template>
  <div class="reference-view">
    <!-- 顶部导航栏 -->
    <header class="top-header">
      <div class="header-left">
        <h1 class="page-title">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
            <polyline points="14 2 14 8 20 8"></polyline>
            <line x1="16" y1="13" x2="8" y2="13"></line>
            <line x1="16" y1="17" x2="8" y2="17"></line>
            <polyline points="10 9 9 9 8 9"></polyline>
          </svg>
          笔记素材库
        </h1>
        <SourceSegmentedControl
          v-model="store.sourceMode"
          :counts="sourceCounts"
          @update:model-value="handleSourceChange"
        />
      </div>
      <div class="header-actions">
        <!-- 视图切换 -->
        <div class="view-toggle">
          <button
            class="toggle-btn"
            :class="{ active: viewMode === 'list' }"
            @click="viewMode = 'list'"
            title="列表视图"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="8" y1="6" x2="21" y2="6"></line>
              <line x1="8" y1="12" x2="21" y2="12"></line>
              <line x1="8" y1="18" x2="21" y2="18"></line>
              <line x1="3" y1="6" x2="3.01" y2="6"></line>
              <line x1="3" y1="12" x2="3.01" y2="12"></line>
              <line x1="3" y1="18" x2="3.01" y2="18"></line>
            </svg>
          </button>
          <button
            class="toggle-btn"
            :class="{ active: viewMode === 'grid' }"
            @click="viewMode = 'grid'"
            title="网格视图"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="3" y="3" width="7" height="7"></rect>
              <rect x="14" y="3" width="7" height="7"></rect>
              <rect x="14" y="14" width="7" height="7"></rect>
              <rect x="3" y="14" width="7" height="7"></rect>
            </svg>
          </button>
        </div>
        <!-- 每页条数 -->
        <select :value="store.filters.page_size" @change="handlePageSizeChange" class="page-size-select">
          <option :value="20">20 条/页</option>
          <option :value="50">50 条/页</option>
          <option :value="100">100 条/页</option>
          <option :value="200">200 条/页</option>
        </select>
        <!-- 同步按钮 -->
        <button class="sync-btn" @click="handleSync" :disabled="store.loading">
          <svg v-if="!store.loading" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 2v6h-6"></path>
            <path d="M3 12a9 9 0 0 1 15-6.7L21 8"></path>
            <path d="M3 22v-6h6"></path>
            <path d="M21 12a9 9 0 0 1-15 6.7L3 16"></path>
          </svg>
          <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="spin">
            <path d="M21 12a9 9 0 1 1-6.219-8.56"></path>
          </svg>
          {{ store.loading ? '同步中' : '同步数据' }}
        </button>
      </div>
    </header>

    <!-- 主内容区：左侧侧边栏 + 右侧内容 -->
    <div class="main-container">
      <!-- 左侧固定面板 -->
      <aside class="sidebar">
        <!-- 统计卡片 -->
        <div class="sidebar-section stats-section">
          <h3 class="section-title">数据概览</h3>
          <ReferenceStats :stats="store.stats" :compact="true" />
        </div>

        <!-- 行业分布 -->
        <div class="sidebar-section" v-if="hasIndustryData">
          <h3 class="section-title">行业分布</h3>
          <div class="industry-list">
            <div
              v-for="([industry, count]) in sortedIndustries.slice(0, 8)"
              :key="industry"
              class="industry-item"
              :class="{ active: store.filters.industry === industry }"
              @click="toggleIndustryFilter(industry)"
            >
              <span class="industry-name">{{ industry }}</span>
              <span class="industry-count">{{ formatCount(count) }}</span>
            </div>
          </div>
        </div>

        <!-- 快捷筛选 -->
        <div class="sidebar-section filters-section">
          <h3 class="section-title">快捷筛选</h3>
          <QuickFilter
            :filters="store.filters"
            :available-industries="store.availableIndustries"
            :show-advanced="showAdvancedFilter"
            @update:keyword="updateFilter('keyword', $event)"
            @update:industry="updateFilter('industry', $event)"
            @update:noteType="updateFilter('note_type', $event)"
            @toggle:advanced="toggleAdvancedFilter"
            @search="handleSearch"
          />
        </div>

        <!-- 高级筛选 -->
        <ReferenceFilter
          :filters="store.filters"
          :visible="showAdvancedFilter"
          @update:minLikes="updateFilter('min_likes', $event)"
          @update:minSaves="updateFilter('min_saves', $event)"
          @update:sortBy="updateFilter('sort_by', $event)"
          @toggleSortOrder="toggleSortOrder"
          @close="closeAdvancedFilter"
          @apply="handleApplyAdvanced"
          @reset="handleResetAdvanced"
        />
      </aside>

      <!-- 右侧内容区 -->
      <main class="content-area">
        <!-- 排序选项 -->
        <div class="sort-bar">
          <span class="sort-label">排序：</span>
          <div class="sort-options">
            <button
              v-for="option in sortOptions"
              :key="option.value"
              class="sort-option"
              :class="{ active: store.filters.sort_by === option.value }"
              @click="handleSortBy(option.value)"
            >
              {{ option.label }}
            </button>
          </div>
          <button
            class="sort-order"
            :class="{ desc: store.filters.sort_order === 'desc' }"
            @click="toggleSortOrder"
            :title="store.filters.sort_order === 'desc' ? '降序' : '升序'"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="12" y1="5" x2="12" y2="19"></line>
              <polyline points="19 12 12 19 5 12"></polyline>
            </svg>
          </button>
        </div>

        <!-- 记录列表 -->
        <div class="records-container" :class="`view-${viewMode}`">
          <!-- 列表视图 -->
          <div v-if="viewMode === 'list' && !store.loading && store.records.length > 0" class="records-list">
            <ReferenceListItem
              v-for="record in store.records"
              :key="record.record_id"
              :record="record"
              :mode="store.sourceMode"
              @detail="handleShowDetail"
            />
          </div>

          <!-- 网格视图 -->
          <div v-else-if="viewMode === 'grid' && !store.loading && store.records.length > 0" class="records-grid">
            <ReferenceCard
              v-for="record in store.records"
              :key="record.record_id"
              :record="record"
              :mode="store.sourceMode"
              @detail="handleShowDetail"
            />
          </div>

          <!-- 加载状态 -->
          <div v-else-if="store.loading" class="loading-state">
            <div class="loading-spinner"></div>
            <p>加载中...</p>
          </div>

          <!-- 空状态 -->
          <div v-else class="empty-state">
            <div class="empty-icon">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <circle cx="11" cy="11" r="8"></circle>
                <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
              </svg>
            </div>
            <h3>{{ store.hasActiveFilters ? '没有符合条件的记录' : '暂无数据' }}</h3>
            <p>{{ store.hasActiveFilters ? '试试调整筛选条件' : '请先配置飞书工作区并同步数据' }}</p>
            <button v-if="store.hasActiveFilters" class="btn primary" @click="handleResetFilters">
              清空筛选条件
            </button>
          </div>
        </div>

        <!-- 分页 -->
        <div v-if="store.pagination.total > 0" class="pagination">
          <div class="pagination-info">
            <span>第 {{ store.pagination.page }} / {{ totalPages }} 页</span>
            <span class="pagination-divider">·</span>
            <span>共 {{ store.pagination.total }} 条</span>
          </div>
          <div class="pagination-controls">
            <button class="page-btn" :disabled="store.pagination.page <= 1" @click="handlePrevPage">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="15 18 9 12 15 6"></polyline>
              </svg>
              上一页
            </button>
            <input
              type="number"
              :value="jumpPage"
              @input="jumpPage = Number(($event.target as HTMLInputElement).value)"
              @keyup.enter="handleJumpPage"
              class="page-input"
              min="1"
              :max="totalPages"
            />
            <button class="page-btn" :disabled="!store.pagination.has_more" @click="handleNextPage">
              下一页
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="9 18 15 12 9 6"></polyline>
              </svg>
            </button>
          </div>
        </div>
      </main>
    </div>

    <!-- 详情弹窗 -->
    <ReferenceDetailModal
      :visible="showDetailModal"
      :record="store.selectedRecord"
      @close="handleCloseDetail"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useReferenceStore } from '@/stores/reference'
import ReferenceStats from '@/components/reference/ReferenceStats.vue'
import QuickFilter from '@/components/reference/QuickFilter.vue'
import ReferenceFilter from '@/components/reference/ReferenceFilter.vue'
import ReferenceListItem from '@/components/reference/ReferenceListItem.vue'
import ReferenceCard from '@/components/reference/ReferenceCard.vue'
import ReferenceDetailModal from '@/components/reference/ReferenceDetailModal.vue'
import SourceSegmentedControl from '@/components/reference/SourceSegmentedControl.vue'

/**
 * 对标文案查询页面
 *
 * 桌面端优化的宽屏布局：
 * - 左侧固定面板：统计、筛选、行业分布
 * - 右侧宽幅内容区：支持列表/网格双视图切换
 */

const store = useReferenceStore()
const showDetailModal = ref(false)
const showAdvancedFilter = ref(false)
const jumpPage = ref(1)
const viewMode = ref<'list' | 'grid'>('list')

// Source counts for segmented control
const sourceCounts = ref<Record<string, number | undefined>>({
  benchmark: undefined,
  search: undefined
})

// 排序选项
const sortOptions = [
  { label: '最新发布', value: 'created_at' },
  { label: '点赞最多', value: 'likes' },
  { label: '收藏最多', value: 'saves' },
  { label: '评论最多', value: 'comments' },
  { label: '总互动量', value: 'total_engagement' },
  { label: '收藏比', value: 'save_ratio' }
]

// 计算总页数
const totalPages = computed(() => {
  return Math.ceil(store.pagination.total / store.pagination.page_size)
})

// 行业数据
const hasIndustryData = computed(() => {
  return store.stats && Object.keys(store.stats.industry_distribution).length > 0
})

const sortedIndustries = computed(() => {
  if (!store.stats) return []
  const distribution = store.stats.industry_distribution
  return Object.entries(distribution)
    .sort(([, a], [, b]) => b - a)
})

// 格式化数量
function formatCount(count: number): string {
  if (count >= 10000) return (count / 10000).toFixed(1) + 'w'
  if (count >= 1000) return (count / 1000).toFixed(1) + 'k'
  return count.toString()
}

// 初始化
onMounted(async () => {
  console.log('[ReferenceView] Component mounted, initializing...')

  // Fetch initial stats
  await store.fetchStats()

  // Fetch workspace counts (lightweight, doesn't affect records)
  const allCounts = await store.fetchWorkspaceCounts()

  // Map workspace names to mode keys
  const workspaces = store.availableWorkspaces
  sourceCounts.value = {
    benchmark: allCounts[workspaces.benchmark.workspace],
    search: allCounts[workspaces.search.workspace]
  }

  // Fetch current mode records for display
  await store.fetchRecords()

  console.log('[ReferenceView] Initialization complete.')
})

// 更新筛选条件
function updateFilter(key: string, value: any) {
  store.setFilters({ [key]: value })
}

// 快捷筛选立即生效
function handleSearch() {
  store.filters.page = 1
  store.fetchRecords()
}

// 切换高级筛选面板
function toggleAdvancedFilter() {
  showAdvancedFilter.value = !showAdvancedFilter.value
}

// 关闭高级筛选面板
function closeAdvancedFilter() {
  showAdvancedFilter.value = false
}

// 应用高级筛选
function handleApplyAdvanced() {
  store.filters.page = 1
  store.fetchRecords()
  showAdvancedFilter.value = false
}

// 重置高级筛选
function handleResetAdvanced() {
  store.setFilters({
    min_likes: undefined,
    min_saves: undefined
  })
  closeAdvancedFilter()
}

// 重置所有筛选条件
function handleResetFilters() {
  store.resetFilters()
  handleSearch()
}

// 切换排序顺序
function toggleSortOrder() {
  store.setSort(
    store.filters.sort_by,
    store.filters.sort_order === 'desc' ? 'asc' : 'desc'
  )
  store.filters.page = 1
  store.fetchRecords()
}

// 修改每页条数
function handlePageSizeChange(event: Event) {
  const pageSize = Number((event.target as HTMLSelectElement).value)
  store.setPageSize(pageSize)
  store.fetchRecords()
}

// 同步数据
async function handleSync() {
  const result = await store.syncData()
  if (result) {
    await store.fetchStats()
  }
}

// 显示详情
async function handleShowDetail(recordId: string) {
  await store.fetchRecord(recordId)
  showDetailModal.value = true
}

// 关闭详情
function handleCloseDetail() {
  showDetailModal.value = false
  store.clearSelectedRecord()
}

// Handle data source change
async function handleSourceChange(newMode: 'benchmark' | 'search') {
  store.setSourceMode(newMode)
  await store.fetchRecords()
}

// 翻页
function handlePrevPage() {
  if (store.pagination.page > 1) {
    store.goToPage(store.pagination.page - 1)
    store.fetchRecords()
    jumpPage.value = store.pagination.page - 1
  }
}

function handleNextPage() {
  if (store.pagination.has_more) {
    store.goToPage(store.pagination.page + 1)
    store.fetchRecords()
    jumpPage.value = store.pagination.page + 1
  }
}

// 跳转页面
function handleJumpPage() {
  const page = Math.max(1, Math.min(jumpPage.value, totalPages.value))
  if (page !== store.pagination.page) {
    store.goToPage(page)
    store.fetchRecords()
  }
  jumpPage.value = page
}

// 点击行业筛选
function toggleIndustryFilter(industry: string) {
  const currentValue = store.filters.industry
  updateFilter('industry', currentValue === industry ? '' : industry)
  handleSearch()
}

// 按字段排序
function handleSortBy(sortBy: typeof sortOptions[0]['value']) {
  if (store.filters.sort_by === sortBy) {
    toggleSortOrder()
  } else {
    store.setSort(sortBy, 'desc')
    store.filters.page = 1
    store.fetchRecords()
  }
}
</script>

<style scoped>
/* ============================================
   桌面端优化的宽屏布局
   ============================================ */

.reference-view {
  min-height: 100vh;
  background: #f8f7f5;
  display: flex;
  flex-direction: column;
}

/* ============================================
   顶部导航栏
   ============================================ */

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

.result-count {
  display: flex;
  align-items: baseline;
  gap: 4px;
  font-size: 13px;
  color: #666;
}

.count-number {
  font-size: 18px;
  font-weight: 700;
  color: #1a1a1a;
}

.filter-indicator {
  color: var(--primary, #ff2442);
  font-weight: 500;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* 视图切换 */
.view-toggle {
  display: flex;
  background: #f0efed;
  border-radius: 8px;
  padding: 3px;
}

.toggle-btn {
  width: 36px;
  height: 32px;
  border: none;
  background: transparent;
  color: #999;
  cursor: pointer;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.toggle-btn:hover {
  color: #666;
}

.toggle-btn.active {
  background: white;
  color: var(--primary, #ff2442);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
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

/* 同步按钮 */
.sync-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 9px 18px;
  border-radius: 8px;
  border: 1px solid var(--primary, #ff2442);
  background: white;
  color: var(--primary, #ff2442);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.sync-btn:hover:not(:disabled) {
  background: var(--primary, #ff2442);
  color: white;
}

.sync-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.sync-btn svg.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* ============================================
   主容器：左右分栏
   ============================================ */

.main-container {
  display: flex;
  flex: 1;
  gap: 0;
  overflow: hidden;
}

/* ============================================
   左侧边栏
   ============================================ */

.sidebar {
  width: 320px;
  flex-shrink: 0;
  padding: 24px 24px 24px 32px;
  overflow-y: auto;
  border-right: 1px solid #e8e6e3;
  background: white;
}

.sidebar-section {
  margin-bottom: 28px;
}

.sidebar-section:last-child {
  margin-bottom: 0;
}

.section-title {
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: #999;
  margin: 0 0 16px 0;
}

/* 统计区域 */
.stats-section :deep(.reference-stats) {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.stats-section :deep(.stat-card) {
  padding: 14px 16px;
}

.stats-section :deep(.stat-value) {
  font-size: 20px;
}

.stats-section :deep(.distribution-card) {
  display: none;
}

/* 行业列表 */
.industry-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.industry-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.15s;
}

.industry-item:hover {
  background: #f8f7f5;
}

.industry-item.active {
  background: linear-gradient(135deg, rgba(255, 36, 66, 0.1) 0%, rgba(255, 107, 107, 0.1) 100%);
}

.industry-name {
  font-size: 13px;
  color: #333;
}

.industry-item.active .industry-name {
  color: var(--primary, #ff2442);
  font-weight: 600;
}

.industry-count {
  font-size: 12px;
  color: #999;
  font-weight: 500;
}

.industry-item.active .industry-count {
  color: var(--primary, #ff2442);
}

/* 筛选区域 */
.filters-section :deep(.quick-filter) {
  border: none;
  padding: 0;
  background: transparent;
}

.filters-section :deep(.quick-options) {
  flex-direction: column;
  align-items: stretch;
}

.filters-section :deep(.advanced-toggle) {
  margin-left: 0;
  width: 100%;
  justify-content: center;
}

/* 高级筛选面板 */
.sidebar :deep(.advanced-filter) {
  box-shadow: none;
  border: 1px solid #e8e6e3;
}

.sidebar :deep(.filter-body) {
  grid-template-columns: 1fr;
}

/* ============================================
   右侧内容区
   ============================================ */

.content-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 24px 32px;
  overflow: hidden;
}

/* 排序栏 */
.sort-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  padding: 12px 16px;
  background: white;
  border-radius: 10px;
  border: 1px solid #e8e6e3;
}

.sort-label {
  font-size: 13px;
  color: #666;
  font-weight: 500;
}

.sort-options {
  display: flex;
  gap: 4px;
  flex: 1;
}

.sort-option {
  padding: 6px 14px;
  border: none;
  background: transparent;
  color: #666;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.2s;
}

.sort-option:hover {
  color: #333;
  background: #f8f7f5;
}

.sort-option.active {
  color: var(--primary, #ff2442);
  background: linear-gradient(135deg, rgba(255, 36, 66, 0.1) 0%, rgba(255, 107, 107, 0.1) 100%);
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

/* ============================================
   记录容器
   ============================================ */

.records-container {
  flex: 1;
  overflow-y: auto;
  padding-right: 8px;
}

/* 滚动条样式 */
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

/* 列表视图 */
.records-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

/* 网格视图 */
.records-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

/* ============================================
   加载/空状态
   ============================================ */

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
  margin: 0 0 24px 0;
}

.btn {
  padding: 10px 24px;
  border-radius: 8px;
  border: none;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn.primary {
  background: var(--primary, #ff2442);
  color: white;
}

.btn.primary:hover {
  background: #e61e3a;
}

/* ============================================
   分页
   ============================================ */

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

.page-input {
  width: 60px;
  padding: 9px 8px;
  border: 1px solid #e0dedb;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  text-align: center;
}

.page-input:focus {
  outline: none;
  border-color: var(--primary, #ff2442);
}
</style>
