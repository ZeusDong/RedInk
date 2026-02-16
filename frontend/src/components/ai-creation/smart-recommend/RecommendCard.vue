<template>
  <div class="recommend-card" :class="[`match-${matchLevel}`]">
    <!-- 紧凑状态 -->
    <div class="card-compact">
      <div class="card-header">
        <MatchBadge :score="matchScore" :level="matchLevel" :show-score="false" />
        <div class="score-display">
          热度指数
          <span class="score">{{ getHeatScore() }}</span>
        </div>
      </div>

      <div class="card-body">
        <!-- 封面图 -->
        <div class="cover-image">
          <img
            :src="record.cover_url || record.cover_image"
            :alt="record.title"
            @error="handleImageError"
          />
          <div v-if="imageError" class="cover-placeholder">
            <span class="placeholder-icon">📷</span>
            <span class="placeholder-text">暂无封面</span>
          </div>
        </div>

        <!-- 标题 -->
        <h4 class="record-title">{{ record.title }}</h4>

        <!-- 数据指标 -->
        <div class="metrics">
          <span class="metric">👍 {{ formatCount(record.metrics?.likes) }}</span>
          <span class="metric">⭐ {{ formatCount(record.metrics?.saves) }}</span>
          <span class="metric">💬 {{ formatCount(record.metrics?.comments) }}</span>
        </div>

        <!-- 标签 -->
        <div class="tags">
          <span class="tag">{{ record.industry || '未分类' }}</span>
        </div>
      </div>

      <button
        @click="toggleExpanded"
        class="expand-toggle"
        :aria-expanded="expanded"
      >
        {{ expanded ? '收起 ▲' : '展开更多 ▼' }}
      </button>
    </div>

    <!-- 展开状态（过渡动画） -->
    <Transition name="expand">
      <div v-if="expanded" class="card-expanded">
        <RecommendReasons :reasons="recommendReasons" />
        <LearnableElements :elements="learnableElements" />
        <div class="card-actions">
          <button @click="handleViewDetail" class="action-btn secondary">
            查看详情
          </button>
          <button @click="handleApply" class="action-btn primary-outline">
            ✨ 作为参考
          </button>
          <button @click="handleSaveAsTemplate" class="action-btn primary">
            📋 保存为模板
          </button>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { RecommendationItem, MatchLevel } from '@/types/recommendation'
import MatchBadge from './MatchBadge.vue'
import RecommendReasons from './RecommendReasons.vue'
import LearnableElements from './LearnableElements.vue'

interface Props {
  recordId: string
  record: RecommendationItem['record']
  matchScore: number
  matchLevel: MatchLevel
  recommendReasons: string[]
  learnableElements: {
    hook: string
    structure: string
    tone: string
    cta: string
  }
}

const props = defineProps<Props>()

const emit = defineEmits<{
  viewDetail: [recordId: string]
  apply: [recordId: string]
  saveTemplate: [recordId: string, record: Props['record']]
}>()

const expanded = ref(false)
const imageError = ref(false)

function toggleExpanded() {
  expanded.value = !expanded.value
}

function getHeatScore() {
  const metrics = props.record.metrics
  if (!metrics) return 'N/A'

  const score = (metrics.likes || 0) * 1 + (metrics.saves || 0) * 2 + (metrics.comments || 0) * 3

  if (score >= 50000) return '🔥🔥🔥'
  if (score >= 20000) return '🔥🔥'
  if (score >= 5000) return '🔥'
  return '📈'
}

function formatCount(count?: number): string {
  if (!count) return '0'
  if (count >= 10000) return (count / 10000).toFixed(1) + 'w'
  if (count >= 1000) return (count / 1000).toFixed(1) + 'k'
  return count.toString()
}

function handleViewDetail() {
  emit('viewDetail', props.recordId)
}

function handleApply() {
  emit('apply', props.recordId)
}

function handleSaveAsTemplate() {
  emit('saveTemplate', props.recordId, props.record)
}

function handleImageError() {
  imageError.value = true
}
</script>

<style scoped>
.recommend-card {
  background: white;
  border: 1px solid #e8e6e3;
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.2s;
}

.recommend-card.match-high {
  border-color: rgba(255, 36, 66, 0.3);
}

.recommend-card.match-high:hover {
  border-color: var(--primary, #ff2442);
  box-shadow: 0 4px 16px rgba(255, 36, 66, 0.15);
}

.recommend-card.match-medium:hover {
  border-color: #ff9800;
  box-shadow: 0 4px 16px rgba(255, 152, 0, 0.1);
}

.recommend-card.match-low:hover {
  border-color: #999;
  box-shadow: 0 4px 16px rgba(153, 153, 153, 0.1);
}

.card-compact {
  display: flex;
  flex-direction: column;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f8f7f5;
  border-bottom: 1px solid #e8e6e3;
}

.score-display {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #666;
}

.score {
  font-weight: 600;
  font-size: 14px;
}

.card-body {
  padding: 16px;
}

.cover-image {
  position: relative;
  width: 100%;
  aspect-ratio: 3 / 4;
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 12px;
  background: #f0efed;
}

.cover-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cover-placeholder {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f5f5f5 0%, #e8e8e8 100%);
  color: #999;
  gap: 8px;
}

.placeholder-icon {
  font-size: 32px;
  opacity: 0.6;
}

.placeholder-text {
  font-size: 13px;
}

.record-title {
  font-size: 15px;
  font-weight: 600;
  color: #333;
  margin: 0 0 8px 0;
  line-height: 1.4;
}

.metrics {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
}

.metric {
  font-size: 13px;
  color: #666;
}

.tags {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
}

.tag {
  padding: 4px 10px;
  background: #f0efed;
  border-radius: 4px;
  font-size: 12px;
  color: #666;
}

.expand-toggle {
  width: 100%;
  padding: 10px 16px;
  border: none;
  background: #f8f7f5;
  color: #666;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border-top: 1px solid #e8e6e3;
}

.expand-toggle:hover {
  background: #f0efed;
  color: #333;
}

.card-expanded {
  padding: 16px;
  border-top: 1px solid #e8e6e3;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* 展开动画 */
.expand-enter-active,
.expand-leave-active {
  transition: all 0.3s ease;
  overflow: hidden;
}

.expand-enter-from,
.expand-leave-to {
  max-height: 0;
  opacity: 0;
}

.expand-enter-to,
.expand-leave-from {
  max-height: 500px;
  opacity: 1;
}

.card-actions {
  display: flex;
  gap: 8px;
  margin-top: 4px;
  flex-wrap: wrap;
}

.action-btn {
  flex: 1;
  min-width: 80px;
  padding: 10px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn.secondary {
  border: 1px solid #e0dedb;
  background: white;
  color: #333;
}

.action-btn.secondary:hover {
  border-color: var(--primary, #ff2442);
  color: var(--primary, #ff2442);
}

.action-btn.primary-outline {
  border: 1px solid var(--primary, #ff2442);
  background: white;
  color: var(--primary, #ff2442);
}

.action-btn.primary-outline:hover {
  background: rgba(255, 36, 66, 0.05);
}

.action-btn.primary {
  border: none;
  background: var(--primary, #ff2442);
  color: white;
}

.action-btn.primary:hover {
  background: #e61f37;
}
</style>
