<template>
  <div class="summary-view">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1 class="page-title">📊 AI总结</h1>
      <button @click="refreshSummaries" class="refresh-btn">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 2v5a2 2 0 0 1 2h10a2 2 0 0 1 2z" />
          <polyline points="23 4 12 20 16 5" />
        </svg>
        刷新
      </button>
    </div>

    <!-- 行业筛选 -->
    <div class="industry-filters">
      <button
        v-for="industry in industriesWithAll"
        :key="industry"
        class="filter-btn"
        :class="{ active: selectedIndustry === industry }"
        @click="selectIndustry(industry)"
      >
        {{ industry }}
      </button>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>加载中...</p>
    </div>

    <!-- 空状态 -->
    <div v-else-if="!loading && filteredSummaries.length === 0" class="empty-state">
      <div class="empty-icon">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M9 5H7a2 2 0 0 0 2v12a2 2 0 0 0 2h10a2 2 0 0 0 2 2z" />
          <rect x="9" y="3" width="6" height="4" rx="1" />
          <path d="M9 14l2 2 4 4" />
        </svg>
      </div>
      <h3>{{ selectedIndustry || '全部' }}行业暂无总结</h3>
      <p>请先在「对标分析」中完成笔记分析，然后在此生成AI总结</p>
    </div>

    <!-- 总结卡片列表 -->
    <div v-else class="summaries-list">
      <SummaryCard
        v-for="summary in paginatedSummaries"
        :key="summary.id"
        :summary="summary"
        @delete="handleDelete"
      />
    </div>

    <!-- 分页 -->
    <div v-if="totalPages > 1" class="pagination">
      <div class="pagination-info">
        <span>第 {{ currentPage }} / {{ totalPages }} 页</span>
        <span class="pagination-divider">·</span>
        <span>共 {{ filteredSummaries.length }} 条</span>
      </div>
      <div class="pagination-controls">
        <button class="page-btn" :disabled="currentPage <= 1" @click="handlePrevPage">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="15 18 9 12 15 6" />
          </svg>
          上一页
        </button>
        <button class="page-btn" :disabled="currentPage >= totalPages" @click="handleNextPage">
          下一页
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="9 18 15 12 9 6" />
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useSummaryStore } from '@/stores/summary'
import SummaryCard from '@/components/summary/SummaryCard.vue'

/**
 * AI总结页面组件
 *
 * 显示所有AI总结，支持按行业筛选和分页
 */

const summaryStore = useSummaryStore()

// 分页状态
const currentPage = ref(1)
const pageSize = ref(10)

// 所有行业（含"全部"）
const industriesWithAll = computed(() => {
  return ['全部', ...summaryStore.industries]
})

// 选中的行业
const selectedIndustry = computed({
  get: () => summaryStore.selectedIndustry,
  set: (value) => summaryStore.setSelectedIndustry(value)
})

// 过滤后的总结列表
const filteredSummaries = computed(() => summaryStore.summaries)
// 分页后的总结列表
const paginatedSummaries = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredSummaries.value.slice(start, end)
})

// 总页数
const totalPages = computed(() => {
  return Math.ceil(filteredSummaries.value.length / pageSize.value)
})

// 加载状态
const loading = computed(() => summaryStore.loading)

// 选择行业
function selectIndustry(industry: string) {
  selectedIndustry.value = industry
  currentPage.value = 1
}

// 刷新总结列表
async function refreshSummaries() {
  await summaryStore.loadSummaries()
}

// 删除总结
async function handleDelete(summaryId: number) {
  if (confirm('确定要删除这条总结吗？')) {
    await summaryStore.deleteSummary(summaryId)
  }
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

// 初始化加载
onMounted(async () => {
  await summaryStore.initialize()
})
</script>

<style scoped>
.summary-view {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

/* 页面头部 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 24px;
  border-bottom: 1px solid #e8e6e3;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-main, #1a1a1a);
  margin: 0;
}

.refresh-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border: none;
  border-radius: 8px;
  background: white;
  color: var(--text-sub, #666);
  cursor: pointer;
  transition: all 0.2s;
}

.refresh-btn:hover {
  background: #f8f8f8;
  color: var(--primary, #ff2442);
}

.refresh-btn svg {
  color: inherit;
}

/* 行业筛选 */
.industry-filters {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  padding-bottom: 24px;
}

.filter-btn {
  padding: 10px 20px;
  border: 2px solid transparent;
  border-radius: 12px;
  background: white;
  color: var(--text-sub, #666);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.filter-btn:hover {
  border-color: var(--primary, #ff2442);
  background: #fff5f5;
}

.filter-btn.active {
  border-color: var(--primary, #ff2442);
  background: var(--primary, #ff2442);
  color: white;
  font-weight: 500;
}

/* 加载/空状态 */
.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 100px 20px;
  background: #fafafa;
  border-radius: 16px;
  margin: 24px 0;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #eee;
  border-top-color: var(--primary, #ff2442);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-state h3 {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-main, #1a1a1a);
  margin: 0 0 16px;
}

.empty-state p {
  font-size: 14px;
  color: var(--text-sub, #666);
  margin: 8px 0 0;
}

/* 总结列表 */
.summaries-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 分页 */
.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 24px;
  border-top: 1px solid #e8e6e3;
}

.pagination-info {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--text-sub, #666);
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
