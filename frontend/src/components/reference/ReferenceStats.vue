<template>
  <!-- 对标文案统计概览 -->
  <div class="reference-stats">
    <div class="stat-card total">
      <div class="stat-icon">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
          <polyline points="14 2 14 8 20 8"></polyline>
          <line x1="16" y1="13" x2="8" y2="13"></line>
          <line x1="16" y1="17" x2="8" y2="17"></line>
          <polyline points="10 9 9 9 8 9"></polyline>
        </svg>
      </div>
      <div class="stat-content">
        <div class="stat-label">总记录数</div>
        <div class="stat-value">{{ stats?.total_records || 0 }}</div>
      </div>
    </div>

    <div class="stat-card">
      <div class="stat-icon">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
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
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
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
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
        </svg>
      </div>
      <div class="stat-content">
        <div class="stat-label">平均评论</div>
        <div class="stat-value">{{ formatMetric(stats?.avg_comments || 0) }}</div>
      </div>
    </div>

    <!-- 行业分布 -->
    <div class="distribution-card" v-if="hasIndustryData">
      <div class="distribution-header">行业分布</div>
      <div class="distribution-list">
        <div
          v-for="(count, industry) in sortedIndustries"
          :key="industry"
          class="distribution-item"
        >
          <span class="industry-name">{{ industry }}</span>
          <div class="industry-bar">
            <div
              class="industry-bar-fill"
              :style="{ width: (count / maxIndustryCount * 100) + '%' }"
            ></div>
          </div>
          <span class="industry-count">{{ count }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ReferenceStats } from '@/api'
import { computed } from 'vue'

/**
 * 对标文案统计概览组件
 *
 * 显示总记录数、平均互动数据、行业分布等统计信息
 */

// 定义 Props
const props = defineProps<{
  stats: ReferenceStats | null
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

// 计算是否有行业数据
const hasIndustryData = computed(() => {
  return props.stats && Object.keys(props.stats.industry_distribution).length > 0
})

// 排序后的行业列表
const sortedIndustries = computed(() => {
  if (!props.stats) return {}
  const distribution = props.stats.industry_distribution
  return Object.entries(distribution)
    .sort(([, a], [, b]) => b - a)
    .reduce((acc, [industry, count]) => {
      acc[industry] = count
      return acc
    }, {} as Record<string, number>)
})

// 最大行业数量
const maxIndustryCount = computed(() => {
  if (!props.stats) return 0
  return Math.max(...Object.values(props.stats.industry_distribution), 1)
})
</script>

<style scoped>
.reference-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

/* 统计卡片 */
.stat-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  border: 1px solid rgba(0, 0, 0, 0.04);
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-card.total {
  background: linear-gradient(135deg, var(--primary) 0%, #ff6b6b 100%);
  border: none;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f5f5;
  color: var(--text-sub, #666);
}

.stat-card.total .stat-icon {
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

.stat-content {
  flex: 1;
}

.stat-label {
  font-size: 13px;
  color: var(--text-sub, #666);
  margin-bottom: 4px;
}

.stat-card.total .stat-label {
  color: rgba(255, 255, 255, 0.8);
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-main, #1a1a1a);
}

.stat-card.total .stat-value {
  color: white;
}

/* 分布卡片 */
.distribution-card {
  grid-column: 1 / -1;
  background: white;
  border-radius: 12px;
  padding: 20px;
  border: 1px solid rgba(0, 0, 0, 0.04);
}

.distribution-header {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-main, #1a1a1a);
  margin-bottom: 16px;
}

.distribution-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.distribution-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.industry-name {
  width: 100px;
  font-size: 13px;
  color: var(--text-sub, #666);
  flex-shrink: 0;
}

.industry-bar {
  flex: 1;
  height: 8px;
  background: #f5f5f5;
  border-radius: 4px;
  overflow: hidden;
}

.industry-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--primary) 0%, #ff6b6b 100%);
  border-radius: 4px;
  transition: width 0.3s ease;
}

.industry-count {
  width: 40px;
  text-align: right;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-main, #1a1a1a);
}
</style>
