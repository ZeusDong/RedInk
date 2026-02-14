<template>
  <div class="recommend-card">
    <div class="card-header">
      <div class="match-badge" :class="getMatchLevelClass()">
        {{ getMatchLabel() }}
      </div>
      <div class="score-display">
        热度指数
        <span class="score">{{ getHeatScore() }}</span>
      </div>
    </div>

    <div class="card-body">
      <!-- 封面图 -->
      <div class="cover-image">
        <img :src="record.cover_url" :alt="record.title" />
        <div v-if="record.images_count > 1" class="image-count">
          {{ record.images_count }}图
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
        <span class="tag">{{ record.note_type || '图文' }}</span>
      </div>

      <!-- 匹配原因 -->
      <div v-if="matchReasons.length > 0" class="match-reasons">
        <div v-for="reason in matchReasons" :key="reason.type" class="reason-item">
          <span class="reason-icon">{{ getReasonIcon(reason.type) }}</span>
          <span class="reason-text">{{ reason.text }}</span>
        </div>
      </div>
    </div>

    <div class="card-actions">
      <button @click="handleViewDetail" class="action-btn secondary">
        查看详情
      </button>
      <button @click="handleApply" class="action-btn primary">
        应用到创作
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface ReferenceRecord {
  record_id: string
  title: string
  cover_url: string
  images_count?: number
  industry?: string
  note_type?: string
  metrics?: {
    likes?: number
    saves?: number
    comments?: number
  }
}

interface RecommendationData {
  match_score: number
  reasons?: string[]
}

const props = defineProps<{
  record: ReferenceRecord
  matchData: RecommendationData
}>()

const emit = defineEmits<{
  viewDetail: [record: ReferenceRecord]
  apply: [record: ReferenceRecord]
}>()

const matchReasons = computed(() => {
  const reasons: Array<{ type: string; text: string }> = []

  if (props.matchData.match_score > 0.8) {
    reasons.push({
      type: 'high',
      text: `高度相关 (匹配度 ${Math.round(props.matchData.match_score * 100)}%)`
    })
  }

  if (props.matchData.reasons?.includes('industry')) {
    reasons.push({ type: 'industry', text: '行业匹配' })
  }

  if (props.matchData.reasons?.includes('keyword')) {
    reasons.push({ type: 'keyword', text: '包含关键词' })
  }

  if (props.matchData.reasons?.includes('trending')) {
    reasons.push({ type: 'trending', text: '热门内容' })
  }

  return reasons
})

function getMatchLevelClass() {
  const score = props.matchData.match_score
  if (score >= 0.8) return 'high'
  if (score >= 0.5) return 'medium'
  return 'low'
}

function getMatchLabel() {
  const score = props.matchData.match_score
  if (score >= 0.8) return '🔥 高度匹配'
  if (score >= 0.5) return '📌 相关推荐'
  return '💡 可能相关'
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

function getReasonIcon(type: string) {
  const icons: Record<string, string> = {
    high: '🎯',
    industry: '🏷️',
    keyword: '🔑',
    trending: '📈'
  }
  return icons[type] || '•'
}

function formatCount(count?: number): string {
  if (!count) return '0'
  if (count >= 10000) return (count / 10000).toFixed(1) + 'w'
  if (count >= 1000) return (count / 1000).toFixed(1) + 'k'
  return count.toString()
}

function handleViewDetail() {
  emit('viewDetail', props.record)
}

function handleApply() {
  emit('apply', props.record)
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

.recommend-card:hover {
  border-color: var(--primary, #ff2442);
  box-shadow: 0 4px 16px rgba(255, 36, 66, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f8f7f5;
  border-bottom: 1px solid #e8e6e3;
}

.match-badge {
  padding: 4px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
}

.match-badge.high {
  background: rgba(255, 36, 66, 0.1);
  color: var(--primary, #ff2442);
}

.match-badge.medium {
  background: rgba(255, 152, 0, 0.1);
  color: #ff9800;
}

.match-badge.low {
  background: rgba(153, 153, 153, 0.1);
  color: #999;
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

.image-count {
  position: absolute;
  bottom: 8px;
  right: 8px;
  padding: 4px 8px;
  background: rgba(0, 0, 0, 0.6);
  color: white;
  border-radius: 4px;
  font-size: 11px;
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
  margin-bottom: 12px;
}

.tag {
  padding: 4px 10px;
  background: #f0efed;
  border-radius: 4px;
  font-size: 12px;
  color: #666;
}

.match-reasons {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding-top: 8px;
  border-top: 1px solid #f0efed;
}

.reason-item {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  background: rgba(255, 36, 66, 0.05);
  border-radius: 4px;
  font-size: 12px;
  color: var(--primary, #ff2442);
}

.reason-icon {
  font-size: 14px;
}

.reason-text {
  font-size: 12px;
}

.card-actions {
  display: flex;
  gap: 8px;
  padding: 12px 16px;
  border-top: 1px solid #e8e6e3;
}

.action-btn {
  flex: 1;
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

.action-btn.primary {
  border: none;
  background: var(--primary, #ff2442);
  color: white;
}

.action-btn.primary:hover {
  background: #e61f37;
}
</style>
