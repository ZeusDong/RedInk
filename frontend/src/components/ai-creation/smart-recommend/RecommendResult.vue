<template>
  <div class="recommend-result">
    <!-- 结果统计 -->
    <div v-if="recommendations.length > 0" class="result-header">
      <div class="result-stats">
        <span class="stat-item">
          找到 <strong>{{ recommendations.length }}</strong> 条相关推荐
        </span>
        <span v-if="searchTopic" class="search-query">
          关键词：{{ searchTopic }}
        </span>
      </div>
      <div class="result-actions">
        <select v-model="sortBy" @change="handleSortChange" class="sort-select">
          <option value="relevance">相关性排序</option>
          <option value="heat">热度排序</option>
          <option value="likes">点赞数</option>
        </select>
      </div>
    </div>

    <!-- 推荐列表 -->
    <div v-if="recommendations.length > 0" class="recommend-list">
      <RecommendCard
        v-for="item in sortedRecommendations"
        :key="item.record_id"
        :record-id="item.record_id"
        :record="item.record"
        :match-score="item.match_score"
        :match-level="item.match_level"
        :recommend-reasons="item.recommend_reasons"
        :learnable-elements="item.learnable_elements"
        @view-detail="handleViewDetail"
        @apply="handleApply"
      />
    </div>

    <!-- 空状态 -->
    <div v-else-if="!loading" class="empty-state">
      <div class="empty-icon">🔍</div>
      <h3>暂无推荐结果</h3>
      <p>请尝试其他关键词或调整筛选条件</p>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>正在分析推荐...</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import RecommendCard from './RecommendCard.vue'
import type { RecommendationItem } from '@/types/recommendation'

const props = defineProps<{
  recommendations: RecommendationItem[]
  loading: boolean
  searchTopic?: string
}>()

const emit = defineEmits<{
  viewDetail: [recordId: string]
  apply: [recordId: string]
}>()

const sortBy = ref<'relevance' | 'heat' | 'likes'>('relevance')

const sortedRecommendations = computed(() => {
  const items = [...props.recommendations]

  switch (sortBy.value) {
    case 'relevance':
      return items.sort((a, b) => b.match_score - a.match_score)
    case 'heat':
      return items.sort((a, b) => {
        const scoreA = (a.record.metrics?.likes || 0) + (a.record.metrics?.saves || 0) * 2
        const scoreB = (b.record.metrics?.likes || 0) + (b.record.metrics?.saves || 0) * 2
        return scoreB - scoreA
      })
    case 'likes':
      return items.sort((a, b) => (b.record.metrics?.likes || 0) - (a.record.metrics?.likes || 0))
    default:
      return items
  }
})

function handleSortChange() {
  // Sort handled by computed property
}

function handleViewDetail(recordId: string) {
  emit('viewDetail', recordId)
}

function handleApply(recordId: string) {
  emit('apply', recordId)
}
</script>

<style scoped>
.recommend-result {
  max-width: 1200px;
  margin: 0 auto;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: white;
  border-radius: 12px;
  margin-bottom: 20px;
}

.result-stats {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-item {
  font-size: 14px;
  color: #333;
}

.stat-item strong {
  color: var(--primary, #ff2442);
  font-weight: 600;
}

.search-query {
  padding: 4px 12px;
  background: rgba(255, 36, 66, 0.1);
  border-radius: 20px;
  font-size: 13px;
  color: var(--primary, #ff2442);
}

.result-actions {
  display: flex;
  gap: 12px;
}

.sort-select {
  padding: 8px 16px;
  border: 1px solid #e0dedb;
  border-radius: 8px;
  background: white;
  font-size: 13px;
  color: #333;
  cursor: pointer;
}

.sort-select:focus {
  outline: none;
  border-color: var(--primary, #ff2442);
}

.recommend-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  background: white;
  border-radius: 12px;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.empty-state h3 {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin: 0 0 8px 0;
}

.empty-state p {
  font-size: 14px;
  color: #666;
  margin: 0;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  background: white;
  border-radius: 12px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #f0f0f0;
  border-top-color: var(--primary, #ff2442);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-state p {
  font-size: 14px;
  color: #666;
  margin: 0;
}
</style>
