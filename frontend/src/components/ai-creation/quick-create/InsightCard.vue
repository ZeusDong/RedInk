<template>
  <div
    class="insight-card"
    :class="{ selected: isSelected }"
    @click="handleClick"
  >
    <div class="card-header">
      <span class="card-type">{{ typeLabel }}</span>
      <button
        v-if="isSelected"
        @click.stop="handleDeselect"
        class="deselect-btn"
      >
        ×
      </button>
    </div>

    <div class="card-content">
      <!-- AI 总结内容 -->
      <template v-if="summary">
        <p class="summary-text">{{ truncatedContent }}</p>
        <div class="card-meta">
          <span class="record-count">{{ summary.record_count }} 条笔记</span>
          <span class="industry">{{ summary.industry }}</span>
        </div>
      </template>

      <!-- 笔记内容 -->
      <template v-else-if="record">
        <h5 class="record-title">{{ record.title }}</h5>
        <div class="record-metrics">
          <span class="metric">👍 {{ formatCount(record.metrics?.likes) }}</span>
          <span class="metric">⭐ {{ formatCount(record.metrics?.saves) }}</span>
        </div>
      </template>
    </div>

    <div v-if="isSelected" class="card-applied">
      ✓ 已应用
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Summary } from '@/stores/summary'

interface ReferenceRecord {
  record_id: string
  title: string
  industry?: string
  metrics?: {
    likes?: number
    saves?: number
    total_engagement?: number
  }
}

const props = defineProps<{
  insight: Summary | ReferenceRecord
  type: 'summary' | 'record'
  isSelected?: boolean
}>()

const emit = defineEmits<{
  select: [insight: typeof props.insight]
  deselect: [insight: typeof props.insight]
}>()

const typeLabel = computed(() => {
  return props.type === 'summary' ? '📝 总结' : '📄 笔记'
})

// Type-narrowed computed properties with explicit types
const summary = computed((): Summary | null => {
  return props.type === 'summary' ? (props.insight as Summary) : null
})

const record = computed((): ReferenceRecord | null => {
  return props.type === 'record' ? (props.insight as ReferenceRecord) : null
})

const truncatedContent = computed((): string => {
  if (summary.value) {
    const content = summary.value.content
    return content.length > 100 ? content.slice(0, 100) + '...' : content
  }
  return ''
})

function handleClick() {
  emit('select', props.insight)
}

function handleDeselect() {
  emit('deselect', props.insight)
}

function formatCount(count?: number): string {
  if (!count) return '0'
  if (count >= 10000) return (count / 10000).toFixed(1) + 'w'
  if (count >= 1000) return (count / 1000).toFixed(1) + 'k'
  return count.toString()
}
</script>

<style scoped>
.insight-card {
  position: relative;
  padding: 12px;
  background: #f8f7f5;
  border: 1px solid #e8e6e3;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.insight-card:hover {
  border-color: var(--primary, #ff2442);
  background: white;
}

.insight-card.selected {
  border-color: var(--primary, #ff2442);
  background: linear-gradient(135deg, rgba(255, 36, 66, 0.05) 0%, rgba(255, 107, 107, 0.05) 100%);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.card-type {
  font-size: 11px;
  font-weight: 600;
  color: #999;
  text-transform: uppercase;
}

.deselect-btn {
  width: 20px;
  height: 20px;
  border: none;
  background: var(--primary, #ff2442);
  color: white;
  border-radius: 50%;
  cursor: pointer;
  font-size: 14px;
  line-height: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.summary-text {
  font-size: 13px;
  color: #333;
  line-height: 1.5;
  margin: 0 0 8px 0;
}

.record-title {
  font-size: 13px;
  font-weight: 600;
  color: #333;
  margin: 0 0 8px 0;
  line-height: 1.4;
}

.card-meta,
.record-metrics {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: #666;
}

.record-metrics {
  margin-top: 8px;
}

.metric {
  display: flex;
  align-items: center;
  gap: 2px;
}

.card-applied {
  position: absolute;
  top: 12px;
  right: 12px;
  background: var(--primary, #ff2442);
  color: white;
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 4px;
}
</style>
