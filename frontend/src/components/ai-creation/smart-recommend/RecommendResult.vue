<template>
  <div class="recommend-result">
    <!-- 加载状态（新搜索时显示在输入框下方） -->
    <Transition name="fade-slide">
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>正在分析推荐...</p>
        <div class="loading-steps">
          <span class="step" :class="{ active: loadingStep >= 1 }">🔍 分析主题</span>
          <span class="step-divider">→</span>
          <span class="step" :class="{ active: loadingStep >= 2 }">🎯 匹配内容</span>
          <span class="step-divider">→</span>
          <span class="step" :class="{ active: loadingStep >= 3 }">✨ 生成推荐</span>
        </div>
      </div>
    </Transition>

    <!-- 结果统计 -->
    <div v-if="recommendations.length > 0 && !loading" class="result-header">
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
    <Transition name="fade-list">
      <div v-if="recommendations.length > 0 && !loading" class="recommend-list">
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
    </Transition>

    <!-- 空状态 -->
    <Transition name="fade">
      <div v-if="recommendations.length === 0 && !loading" class="empty-state">
        <div class="empty-icon">🔍</div>
        <h3>暂无推荐结果</h3>
        <p>请尝试其他关键词或调整筛选条件</p>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
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
const loadingStep = ref(0)

// Animate loading steps when loading starts
watch(() => props.loading, (isLoading) => {
  if (isLoading) {
    loadingStep.value = 0
    const steps = [1, 2, 3]
    let delay = 0
    steps.forEach((step) => {
      delay += 400
      setTimeout(() => {
        if (props.loading) loadingStep.value = step
      }, delay)
    })
  } else {
    loadingStep.value = 0
  }
})

// Define match level priority for sorting
const matchLevelPriority: Record<string, number> = {
  high: 3,
  medium: 2,
  low: 1
}

const sortedRecommendations = computed(() => {
  const items = [...props.recommendations]

  switch (sortBy.value) {
    case 'relevance':
      // Sort by match_level first (high > medium > low), then by match_score
      return items.sort((a, b) => {
        const levelDiff = matchLevelPriority[b.match_level] - matchLevelPriority[a.match_level]
        if (levelDiff !== 0) return levelDiff
        return b.match_score - a.match_score
      })
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

/* Loading State with Progress Steps */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 32px;
  background: white;
  border-radius: 16px;
  margin-bottom: 24px;
  box-shadow: 0 4px 20px rgba(255, 36, 66, 0.08);
}

.spinner {
  width: 48px;
  height: 48px;
  border: 4px solid #f0f0f0;
  border-top-color: var(--primary, #ff2442);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-state p {
  font-size: 15px;
  color: #333;
  margin: 0 0 20px 0;
  font-weight: 500;
}

.loading-steps {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}

.step {
  color: #ccc;
  transition: all 0.3s ease;
  padding: 6px 12px;
  border-radius: 6px;
}

.step.active {
  color: var(--primary, #ff2442);
  background: rgba(255, 36, 66, 0.08);
  font-weight: 600;
}

.step-divider {
  color: #ddd;
  transition: color 0.3s ease;
}

.step.active + .step-divider,
.step.active ~ .step.active + .step-divider {
  color: var(--primary, #ff2442);
}

/* Result Header */
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

/* Transitions */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.3s ease;
}

.fade-slide-enter-from,
.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.fade-list-enter-active {
  transition: all 0.4s ease;
}

.fade-list-enter-from {
  opacity: 0;
  transform: translateY(20px);
}
</style>
