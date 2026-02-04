<template>
  <div class="reference-view">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-title">
        <h1>对标文案查询</h1>
        <p class="header-subtitle">从飞书多维表格中查询和浏览小红书对标内容数据</p>
      </div>
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
        {{ store.loading ? '同步中...' : '同步数据' }}
      </button>
    </div>

    <!-- 统计概览 -->
    <ReferenceStats :stats="store.stats" />

    <!-- 主要内容区 -->
    <div class="reference-main">
      <!-- 筛选侧边栏 -->
      <aside class="reference-sidebar">
        <ReferenceFilter
          :filters="store.filters"
          :available-industries="store.availableIndustries"
          @update:keyword="updateFilter('keyword', $event)"
          @update:industry="updateFilter('industry', $event)"
          @update:noteType="updateFilter('note_type', $event)"
          @update:minLikes="updateFilter('min_likes', $event)"
          @update:minSaves="updateFilter('min_saves', $event)"
          @update:sortBy="updateFilter('sort_by', $event)"
          @toggleSortOrder="toggleSortOrder"
          @search="handleSearch"
          @reset="handleResetFilters"
        />
      </aside>

      <!-- 记录列表 -->
      <main class="reference-content">
        <!-- 工具栏 -->
        <div class="content-toolbar">
          <div class="toolbar-info">
            共 <span class="info-count">{{ store.pagination.total }}</span> 条记录
            <span v-if="store.hasActiveFilters" class="info-filtered">
              (已筛选)
            </span>
          </div>
          <div class="toolbar-actions">
            <select :value="store.filters.sort_by" @change="updateFilter('sort_by', ($event.target as HTMLSelectElement).value)">
              <option value="created_at">最新发布</option>
              <option value="likes">点赞最多</option>
              <option value="saves">收藏最多</option>
              <option value="comments">评论最多</option>
              <option value="total_engagement">总互动量</option>
              <option value="save_ratio">收藏互动比</option>
            </select>
          </div>
        </div>

        <!-- 记录网格 -->
        <div v-if="!store.loading && store.records.length > 0" class="records-grid">
          <ReferenceCard
            v-for="record in store.records"
            :key="record.record_id"
            :record="record"
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
          <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
            <circle cx="11" cy="11" r="8"></circle>
            <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
          </svg>
          <h3>{{ store.hasActiveFilters ? '没有符合条件的记录' : '暂无数据' }}</h3>
          <p>{{ store.hasActiveFilters ? '试试调整筛选条件' : '请先配置飞书工作区并同步数据' }}</p>
          <button v-if="store.hasActiveFilters" class="btn primary" @click="handleResetFilters">
            清空筛选条件
          </button>
        </div>

        <!-- 分页 -->
        <div v-if="store.pagination.total > 0" class="pagination">
          <button
            class="page-btn"
            :disabled="store.pagination.page <= 1"
            @click="handlePrevPage"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="15 18 9 12 15 6"></polyline>
            </svg>
          </button>
          <span class="page-info">{{ store.pagination.page }} / {{ totalPages }}</span>
          <button
            class="page-btn"
            :disabled="!store.pagination.has_more"
            @click="handleNextPage"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="9 18 15 12 9 6"></polyline>
            </svg>
          </button>
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
import { computed, onMounted, ref, watch } from 'vue'
import { useReferenceStore } from '@/stores/reference'
import ReferenceStats from '@/components/reference/ReferenceStats.vue'
import ReferenceFilter from '@/components/reference/ReferenceFilter.vue'
import ReferenceCard from '@/components/reference/ReferenceCard.vue'
import ReferenceDetailModal from '@/components/reference/ReferenceDetailModal.vue'

/**
 * 对标文案查询页面
 *
 * 提供对标文案的查询、筛选、排序、详情查看等功能
 */

const store = useReferenceStore()
const showDetailModal = ref(false)

// 计算总页数
const totalPages = computed(() => {
  return Math.ceil(store.pagination.total / store.pagination.page_size)
})

// 初始化
onMounted(async () => {
  // 加载统计信息
  await store.fetchStats()
  // 加载记录列表
  await store.fetchRecords()
})

// 更新筛选条件
function updateFilter(key: string, value: any) {
  store.setFilters({ [key]: value })
  store.filters.page = 1  // 重置到第一页
  handleSearch()
}

// 切换排序顺序
function toggleSortOrder() {
  store.setSort(
    store.filters.sort_by,
    store.filters.sort_order === 'desc' ? 'asc' : 'desc'
  )
  handleSearch()
}

// 搜索
function handleSearch() {
  store.fetchRecords()
}

// 重置筛选条件
function handleResetFilters() {
  store.resetFilters()
  handleSearch()
}

// 同步数据
async function handleSync() {
  const result = await store.syncData()
  if (result) {
    // 重新加载统计信息
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

// 翻页
function handlePrevPage() {
  if (store.pagination.page > 1) {
    store.goToPage(store.pagination.page - 1)
    store.fetchRecords()
  }
}

function handleNextPage() {
  if (store.pagination.has_more) {
    store.goToPage(store.pagination.page + 1)
    store.fetchRecords()
  }
}
</script>

<style scoped>
.reference-view {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px;
}

/* 页面头部 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}

.header-title h1 {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-main, #1a1a1a);
  margin: 0 0 8px 0;
}

.header-subtitle {
  font-size: 14px;
  color: var(--text-sub, #666);
  margin: 0;
}

.sync-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border-radius: 8px;
  border: 1px solid var(--primary, #ff2442);
  background: white;
  color: var(--primary, #ff2442);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.sync-btn:hover:not(:disabled) {
  background: var(--primary, #ff2442);
  color: white;
}

.sync-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.sync-btn svg.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* 主要内容区 */
.reference-main {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 24px;
}

/* 侧边栏 */
.reference-sidebar {
  position: sticky;
  top: 24px;
  align-self: start;
}

/* 内容区 */
.reference-content {
  min-height: 500px;
}

/* 工具栏 */
.content-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 16px;
  background: white;
  border-radius: 12px;
  border: 1px solid rgba(0, 0, 0, 0.04);
}

.toolbar-info {
  font-size: 14px;
  color: var(--text-sub, #666);
}

.info-count {
  font-weight: 600;
  color: var(--text-main, #1a1a1a);
}

.info-filtered {
  color: var(--primary, #ff2442);
}

.toolbar-actions select {
  padding: 8px 32px 8px 12px;
  border: 1px solid #e5e5e5;
  border-radius: 6px;
  background: white;
  font-size: 14px;
  color: var(--text-main, #1a1a1a);
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%23666' stroke-width='2'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 8px center;
  padding-right: 32px;
}

/* 记录网格 */
.records-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

/* 加载状态 */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  color: var(--text-sub, #666);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #f0f0f0;
  border-top-color: var(--primary, #ff2442);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  color: var(--text-placeholder, #ccc);
}

.empty-state svg {
  margin-bottom: 16px;
}

.empty-state h3 {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-sub, #666);
  margin: 0 0 8px 0;
}

.empty-state p {
  font-size: 14px;
  color: var(--text-placeholder, #ccc);
  margin: 0 0 20px 0;
}

/* 分页 */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  padding: 20px 0;
}

.page-btn {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  border: 1px solid #e5e5e5;
  background: white;
  color: var(--text-sub, #666);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
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

.page-info {
  font-size: 14px;
  color: var(--text-sub, #666);
  min-width: 60px;
  text-align: center;
}

/* 按钮样式 */
.btn {
  padding: 10px 24px;
  border-radius: 8px;
  border: none;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn.primary {
  background: var(--primary, #ff2442);
  color: white;
}

.btn.primary:hover {
  background: var(--primary-hover, #e61e3a);
}

/* 响应式 */
@media (max-width: 1024px) {
  .reference-main {
    grid-template-columns: 1fr;
  }

  .reference-sidebar {
    position: static;
    margin-bottom: 24px;
  }
}

@media (max-width: 768px) {
  .reference-view {
    padding: 16px;
  }

  .page-header {
    flex-direction: column;
    gap: 16px;
  }

  .records-grid {
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  }
}
</style>
