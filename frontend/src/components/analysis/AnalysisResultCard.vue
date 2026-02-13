<template>
  <!-- 分析结果卡片 -->
  <div
    class="analysis-result-card"
    :class="{ selected: isSelected, 'batch-mode': batchSelectionEnabled }"
  >
    <!-- 批量选择复选框 -->
    <div
      v-if="batchSelectionEnabled"
      class="batch-checkbox"
      @click.stop="$emit('toggle-select', record.record_id)"
    >
      <svg
        v-if="isBatchSelected"
        width="20"
        height="20"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
      >
        <rect x="3" y="3" width="18" height="18" rx="2" />
        <path d="M9 12l2 2 4-4" />
      </svg>
      <svg
        v-else
        width="20"
        height="20"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
      >
        <rect x="3" y="3" width="18" height="18" rx="2" />
      </svg>
    </div>

    <!-- 点击选择卡片 -->
    <div class="card-content" @click="$emit('select', record.record_id)">
      <div class="card-cover">
        <img
          v-if="record.cover_image"
          :src="record.cover_image"
          alt="cover"
          loading="lazy"
          decoding="async"
        />
        <div v-else class="cover-placeholder">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
            <circle cx="8.5" cy="8.5" r="1.5"></circle>
            <polyline points="21 15 16 10 5 21"></polyline>
          </svg>
        </div>

        <!-- 已分析标记 -->
        <div class="analyzed-badge">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
            <polyline points="22 4 12 14.01 9 11.01"></polyline>
          </svg>
          已分析
        </div>
      </div>
    </div>

    <!-- 底部信息 -->
    <div class="card-footer">
      <div class="card-title" :title="record.title">{{ record.title || '无标题' }}</div>

      <!-- 博主信息 -->
      <div class="blogger-info" v-if="record.blogger?.nickname">
        <img
          v-if="record.blogger.avatar"
          :src="record.blogger.avatar"
          alt="avatar"
          class="blogger-avatar"
        />
        <div v-else class="blogger-avatar-placeholder">
          {{ record.blogger.nickname.charAt(0) }}
        </div>
        <span class="blogger-name">{{ record.blogger.nickname }}</span>
      </div>

      <!-- 互动数据 -->
      <div class="metrics">
        <span class="metric-item">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
          </svg>
          {{ formatMetric(record.metrics?.likes || 0) }}
        </span>
        <span class="metric-item">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path>
          </svg>
          {{ formatMetric(record.metrics?.saves || 0) }}
        </span>
        <span class="metric-item">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
          </svg>
          {{ formatMetric(record.metrics?.comments || 0) }}
        </span>
      </div>

      <!-- 标签 -->
      <div class="tags" v-if="record.tags && record.tags.length">
        <span class="tag" v-for="tag in record.tags.slice(0, 3)" :key="tag">
          {{ tag }}
        </span>
        <span v-if="record.tags.length > 3" class="tag-more">
          +{{ record.tags.length - 3 }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { ReferenceRecord } from '@/api'

/**
 * 分析结果卡片组件
 *
 * 与 AnalysisCard 类似，但显示"已分析"标记，点击选择记录
 */
const props = defineProps<{
  record: ReferenceRecord
  isSelected: boolean
  batchSelectionEnabled?: boolean
}>()

const emit = defineEmits<{
  (e: 'select', id: string): void
  (e: 'toggle-select', id: string): void
}>()

const isBatchSelected = computed(() => props.isSelected)


/**
 * 格式化互动数据
 */
function formatMetric(count: number): string {
  if (count >= 10000) {
    return (count / 10000).toFixed(1) + 'w'
  }
  if (count >= 1000) {
    return (count / 1000).toFixed(1) + 'k'
  }
  return count.toString()
}
</script>

<style scoped>
/* 卡片容器 */
.analysis-result-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  border: 2px solid transparent;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  cursor: pointer;
}

.analysis-result-card:hover {
  transform: translateY(-4px) translateZ(0);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.08);
}

.analysis-result-card.selected {
  border-color: var(--primary, #ff2442);
  box-shadow: 0 0 0 4px rgba(255, 36, 66, 0.1);
}

/* 封面区域 */
.card-cover {
  aspect-ratio: 3/4;
  background: #f7f7f7;
  position: relative;
  overflow: hidden;
}

.card-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.analysis-result-card:hover .card-cover img {
  transform: scale(1.05) translateZ(0);
}

/* 封面占位符 */
.cover-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #e0e0e0;
  background: #fafafa;
}

/* 已分析标记 */
.analyzed-badge {
  position: absolute;
  top: 10px;
  left: 10px;
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  background: rgba(34, 197, 94, 0.95);
  backdrop-filter: blur(4px);
  border-radius: 6px;
  color: white;
  font-size: 12px;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.analyzed-badge svg {
  flex-shrink: 0;
}

/* 底部区域 */
.card-footer {
  padding: 16px;
}

.card-title {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 12px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  color: var(--text-main, #1a1a1a);
}

/* 博主信息 */
.blogger-info {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.blogger-avatar,
.blogger-avatar-placeholder {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  object-fit: cover;
}

.blogger-avatar-placeholder {
  background: linear-gradient(135deg, var(--primary) 0%, #ff6b6b 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 12px;
  font-weight: 600;
}

.blogger-name {
  font-size: 13px;
  color: var(--text-main, #1a1a1a);
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 互动数据 */
.metrics {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
}

.metric-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: var(--text-sub, #666);
}

.metric-item svg {
  color: var(--text-placeholder, #ccc);
}

/* 标签 */
.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.tag {
  padding: 4px 10px;
  border-radius: 4px;
  background: #f5f5f5;
  font-size: 11px;
  color: var(--text-sub, #666);
}

.tag-more {
  padding: 4px 8px;
  border-radius: 4px;
  background: #f0f0f0;
  font-size: 11px;
  color: var(--text-placeholder, #999);
}

/* 批量选择模式 */
.analysis-result-card.batch-mode {
  cursor: default;
}

.batch-checkbox {
  position: absolute;
  top: 10px;
  left: 10px;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 8px;
  cursor: pointer;
  z-index: 10;
  transition: all 0.2s;
}

.batch-checkbox:hover {
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.batch-checkbox svg {
  color: var(--primary, #ff2442);
}

.card-content {
  display: flex;
  flex-direction: column;
}

.batch-mode .card-content {
  cursor: pointer;
}
</style>
