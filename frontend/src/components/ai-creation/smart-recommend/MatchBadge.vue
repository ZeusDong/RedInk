<template>
  <div class="match-badge" :class="[`level-${level}`]">
    <span class="badge-icon">{{ icon }}</span>
    <span class="badge-label">{{ label }}</span>
    <span v-if="showScore" class="badge-score">{{ Math.round(score * 100) }}%</span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { MatchLevel } from '@/types/recommendation'

interface Props {
  score: number
  level: MatchLevel
  showScore?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showScore: false
})

const icon = computed(() => {
  switch (props.level) {
    case 'high':
      return '🔥'
    case 'medium':
      return '📌'
    case 'low':
      return '💡'
    default:
      return '📌'
  }
})

const label = computed(() => {
  switch (props.level) {
    case 'high':
      return '高度匹配'
    case 'medium':
      return '相关推荐'
    case 'low':
      return '可能相关'
    default:
      return '相关推荐'
  }
})
</script>

<style scoped>
.match-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  transition: all 0.2s ease;
}

.match-badge.level-high {
  background: linear-gradient(135deg, rgba(255, 36, 66, 0.1) 0%, rgba(255, 87, 51, 0.1) 100%);
  color: var(--primary, #ff2442);
  border: 1px solid rgba(255, 36, 66, 0.2);
}

.match-badge.level-medium {
  background: linear-gradient(135deg, rgba(255, 152, 0, 0.1) 0%, rgba(255, 193, 7, 0.1) 100%);
  color: #ff9800;
  border: 1px solid rgba(255, 152, 0, 0.2);
}

.match-badge.level-low {
  background: linear-gradient(135deg, rgba(153, 153, 153, 0.1) 0%, rgba(189, 189, 189, 0.1) 100%);
  color: #999;
  border: 1px solid rgba(153, 153, 153, 0.2);
}

.badge-icon {
  font-size: 14px;
  line-height: 1;
}

.badge-label {
  line-height: 1;
}

.badge-score {
  margin-left: 4px;
  padding-left: 8px;
  border-left: 1px solid currentColor;
  font-size: 12px;
  opacity: 0.8;
}
</style>
