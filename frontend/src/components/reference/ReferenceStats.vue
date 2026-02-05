<template>
  <!-- 对标文案统计概览 -->
  <div class="reference-stats" :class="{ compact: compact }">
    <div class="stat-card total">
      <div class="stat-icon">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
          <polyline points="14 2 14 8 20 8"></polyline>
        </svg>
      </div>
      <div class="stat-content">
        <div class="stat-label">总记录</div>
        <div class="stat-value">{{ stats?.total_records || 0 }}</div>
      </div>
    </div>

    <div class="stat-card">
      <div class="stat-icon">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
        </svg>
      </div>
      <div class="stat-content">
        <div class="stat-label">平均点赞</div>
        <div class="stat-value">{{ formatMetric(stats?.avg_likes || 0) }}</div>
      </div>
    </div>

    <div class="stat-card">
      <div class="stat-icon">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path>
        </svg>
      </div>
      <div class="stat-content">
        <div class="stat-label">平均收藏</div>
        <div class="stat-value">{{ formatMetric(stats?.avg_saves || 0) }}</div>
      </div>
    </div>

    <div class="stat-card">
      <div class="stat-icon">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
        </svg>
      </div>
      <div class="stat-content">
        <div class="stat-label">平均评论</div>
        <div class="stat-value">{{ formatMetric(stats?.avg_comments || 0) }}</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ReferenceStats } from '@/api'

/**
 * 对标文案统计概览组件
 *
 * 显示总记录数、平均互动数据等统计信息
 * 支持紧凑模式（侧边栏使用）和标准模式
 */

// 定义 Props
const props = defineProps<{
  stats: ReferenceStats | null
  compact?: boolean
}>()

/**
 * 格式化数值
 */
function formatMetric(value: number): string {
  if (value >= 10000) {
    return (value / 10000).toFixed(1) + 'w'
  }
  if (value >= 1000) {
    return (value / 1000).toFixed(1) + 'k'
  }
  return value.toFixed(0)
}
</script>

<style scoped>
.reference-stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

/* 紧凑模式（侧边栏） */
.reference-stats.compact {
  gap: 8px;
}

/* 统计卡片 */
.stat-card {
  background: white;
  border-radius: 10px;
  padding: 14px;
  border: 1px solid #e8e6e3;
  display: flex;
  align-items: center;
  gap: 12px;
  transition: all 0.2s;
}

.stat-card:hover {
  border-color: #d0cdc9;
}

.stat-card.total {
  background: linear-gradient(135deg, var(--primary) 0%, #ff6b6b 100%);
  border: none;
}

.stat-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8f7f5;
  color: #666;
  flex-shrink: 0;
}

.stat-card.total .stat-icon {
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

.stat-content {
  flex: 1;
  min-width: 0;
}

.stat-label {
  font-size: 11px;
  color: #666;
  margin-bottom: 2px;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.stat-card.total .stat-label {
  color: rgba(255, 255, 255, 0.85);
}

.stat-value {
  font-size: 20px;
  font-weight: 700;
  color: #1a1a1a;
  line-height: 1;
}

.stat-card.total .stat-value {
  color: white;
}

/* 紧凑模式调整 */
.reference-stats.compact .stat-card {
  padding: 12px;
  gap: 10px;
}

.reference-stats.compact .stat-icon {
  width: 36px;
  height: 36px;
}

.reference-stats.compact .stat-icon svg {
  width: 16px;
  height: 16px;
}

.reference-stats.compact .stat-value {
  font-size: 18px;
}

.reference-stats.compact .stat-label {
  font-size: 10px;
}
</style>
