<template>
  <!-- 对标分析卡片 -->
  <div class="analysis-card" @click="$emit('detail', record.record_id)">
    <!-- 封面区域 -->
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

      <!-- 悬浮操作按钮 -->
      <div class="card-overlay">
        <button class="overlay-btn analyze-btn" @click.stop="$emit('analyze', record.record_id)">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2"></path>
            <rect x="9" y="3" width="6" height="4" rx="1"></rect>
            <path d="M9 14l2 2 4-4"></path>
          </svg>
          对标分析
        </button>
        <a
          v-if="record.note_link"
          :href="record.note_link"
          target="_blank"
          rel="noopener noreferrer"
          class="overlay-btn"
          @click.stop
        >
          打开原文
        </a>
      </div>
    </div>

    <!-- 底部信息 -->
    <div class="card-footer">
      <div class="card-title" :title="record.title">{{ record.title || '无标题' }}</div>

      <!-- 博主信息 -->
      <div class="blogger-info" v-if="record.blogger.nickname">
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
          {{ formatMetric(record.metrics.likes) }}
        </span>
        <span class="metric-item">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path>
          </svg>
          {{ formatMetric(record.metrics.saves) }}
        </span>
        <span class="metric-item">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
          </svg>
          {{ formatMetric(record.metrics.comments) }}
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
import type { ReferenceRecord } from '@/api'

/**
 * 对标分析卡片组件
 *
 * 与 ReferenceCard 类似，但带有"对标分析"按钮
 */
const props = defineProps<{
  record: ReferenceRecord
}>()

defineEmits<{
  (e: 'detail', id: string): void
  (e: 'analyze', id: string): void
}>()

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
.analysis-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid rgba(0, 0, 0, 0.04);
  transition: transform 0.2s cubic-bezier(0.4, 0, 0.2, 1),
              box-shadow 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  cursor: pointer;
}

.analysis-card:hover {
  transform: translateY(-4px) translateZ(0);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.08);
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

.analysis-card:hover .card-cover img {
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

/* 悬浮遮罩层 */
.card-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  opacity: 0;
  transition: opacity 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  backdrop-filter: blur(2px);
  pointer-events: none;
}

.analysis-card:hover .card-overlay {
  opacity: 1;
  pointer-events: auto;
}

/* 遮罩层按钮 */
.overlay-btn {
  padding: 8px 24px;
  border-radius: 100px;
  border: 1px solid rgba(255, 255, 255, 0.8);
  background: rgba(255, 255, 255, 0.2);
  color: white;
  font-size: 14px;
  cursor: pointer;
  text-decoration: none;
  transition: background-color 0.2s, color 0.2s, transform 0.1s;
  display: flex;
  align-items: center;
  gap: 6px;
}

.overlay-btn:hover {
  background: white;
  color: var(--text-main, #1a1a1a);
  transform: translateY(-2px);
}

.overlay-btn.analyze-btn {
  background: var(--primary, #ff2442);
  border-color: var(--primary, #ff2442);
}

.overlay-btn.analyze-btn:hover {
  background: var(--primary-hover, #e61e3a);
  color: white;
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
</style>
