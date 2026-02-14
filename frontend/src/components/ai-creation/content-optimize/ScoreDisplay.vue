<template>
  <div class="score-display">
    <!-- 总分 -->
    <div class="score-ring">
      <svg class="score-svg" viewBox="0 0 120 120">
        <circle
          cx="60"
          cy="60"
          r="54"
          fill="none"
          stroke="#e8e6e3"
          stroke-width="8"
        />
        <circle
          class="score-circle"
          cx="60"
          cy="60"
          r="54"
          fill="none"
          :stroke="scoreColor"
          stroke-width="8"
          :stroke-dasharray="circumference"
          transform="rotate(-90 60 60)"
        />
        <text x="60" y="60" text-anchor="middle" dominant-baseline="middle" :fill="scoreColor">
          {{ score }}
        </text>
      </svg>
    </div>

    <!-- 分数详情 -->
    <div class="score-breakdown">
      <div
        v-for="(value, key) in breakdown"
        :key="key"
        class="score-item"
      >
        <span class="score-label">{{ getLabel(key) }}</span>
        <span class="score-bar" :class="getScoreClass(key)">
          <span class="score-fill" :style="{ width: value + '%' }"></span>
          <span class="score-value">{{ value }}</span>
        </span>
      </div>
    </div>

    <!-- 改进提示 -->
    <div v-if="improvement > 0" class="improvement-hint">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <polyline points="22 11 15 7 13 5 13"></polyline>
      </svg>
      <span>优化后可提升 {{ improvement }}%</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface ContentScore {
  total: number
  breakdown: {
    title: number
    structure: number
    visual: number
    engagement: number
  }
}

const props = defineProps<{
  score: ContentScore | null
  improvement?: number
}>()

const score = computed(() => props.score ? Math.round(props.score.total) : 0)
const breakdown = computed(() => props.score?.breakdown ?? {})
const improvement = computed(() => props.improvement || 0)

const circumference = computed(() => {
  // 圆周长 = 2 * PI * r
  return 2 * Math.PI * 54
})

const scoreColor = computed(() => {
  const s = score.value
  if (s >= 80) return '#10b981'  // 绿色
  if (s >= 60) return '#ffa500'  // 橙色
  return '#ff2442'  // 红色
})

function getLabel(key: string): string {
  const labels: Record<string, string> = {
    title: '标题',
    structure: '结构',
    visual: '视觉',
    engagement: '互动性'
  }
  return labels[key] || key
}

function getScoreClass(key: string): string {
  const value = breakdown.value[key as keyof typeof breakdown.value]
  if (!value) return 'poor'
  if (value >= 80) return 'excellent'
  if (value >= 60) return 'good'
  if (value >= 40) return 'fair'
  return 'poor'
}
</script>

<style scoped>
.score-display {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24px;
  padding: 24px;
  background: white;
  border-radius: 12px;
}

.score-ring {
  position: relative;
  width: 140px;
  height: 140px;
}

.score-svg {
  width: 100%;
  height: 100%;
}

.score-circle {
  transition: stroke-dashoffset 1s ease-out;
}

.score-ring text {
  font-size: 28px;
  font-weight: 700;
  fill: currentColor;
}

.score-breakdown {
  display: flex;
  flex-direction: column;
  gap: 12px;
  width: 100%;
}

.score-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.score-label {
  font-size: 13px;
  color: #666;
  width: 80px;
}

.score-bar {
  position: relative;
  flex: 1;
  height: 24px;
  background: #f0f0f0;
  border-radius: 12px;
  overflow: hidden;
}

.score-fill {
  height: 100%;
  background: currentColor;
  border-radius: 12px;
  transition: width 0.5s ease-out;
}

.score-value {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 12px;
  font-weight: 600;
  color: #333;
}

.score-bar.excellent .score-fill {
  background: #10b981;
}

.score-bar.good .score-fill {
  background: #ffa500;
}

.score-bar.fair .score-fill {
  background: #ff9800;
}

.score-bar.poor .score-fill {
  background: #ff2442;
}

.improvement-hint {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: rgba(16, 185, 129, 0.1);
  border-radius: 20px;
  font-size: 13px;
  color: #10b981;
  font-weight: 500;
}

.improvement-hint svg {
  flex-shrink: 0;
}
</style>
