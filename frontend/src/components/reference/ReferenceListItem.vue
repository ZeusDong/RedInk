<template>
  <!-- 列表项卡片 - 桌面宽屏布局 -->
  <div class="list-item-card" @click="$emit('detail', record.record_id)">
    <!-- 封面图 -->
    <div class="item-cover" v-if="record.cover_image">
      <img
        :src="record.cover_image"
        alt="cover"
        loading="lazy"
        decoding="async"
      />
    </div>
    <div class="item-cover placeholder" v-else>
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
        <circle cx="8.5" cy="8.5" r="1.5"></circle>
        <polyline points="21 15 16 10 5 21"></polyline>
      </svg>
    </div>

    <!-- 内容区域 -->
    <div class="item-content">
      <!-- 标题行 -->
      <div class="item-header">
        <div class="item-title" :title="record.title">
          {{ record.title || '无标题' }}
        </div>
        <div class="item-badges">
          <span v-if="record.note_type" class="badge type-badge">{{ record.note_type }}</span>
          <span v-if="record.industry" class="badge industry-badge">{{ record.industry }}</span>
        </div>
      </div>

      <!-- 正文预览 -->
      <div class="item-preview" v-if="record.body">
        {{ record.body }}
      </div>

      <!-- 标签行 -->
      <div class="item-tags" v-if="record.tags && record.tags.length || (record.keyword && mode === 'search') || (isBenchmarkMode && hasTargetFlag)">
        <span v-if="record.keyword && mode === 'search'" class="inline-tag keyword">
          🔍 {{ record.keyword }}
        </span>
        <span v-else-if="isBenchmarkMode && hasTargetFlag" class="inline-tag target">
          待二创
        </span>
        <span class="tag" v-for="tag in record.tags.slice(0, 5)" :key="tag">
          #{{ tag }}
        </span>
        <span v-if="record.tags.length > 5" class="tag-more">
          +{{ record.tags.length - 5 }}
        </span>
      </div>

      <!-- 底部信息行 -->
      <div class="item-footer">
        <!-- 博主信息 -->
        <div class="blogger-info" v-if="record.blogger.nickname">
          <img
            v-if="record.blogger.avatar"
            :src="record.blogger.avatar"
            alt="avatar"
            class="blogger-avatar"
          />
          <span v-else class="blogger-avatar-placeholder">
            {{ record.blogger.nickname.charAt(0) }}
          </span>
          <span class="blogger-name">{{ record.blogger.nickname }}</span>
          <span v-if="record.blogger.follower_count" class="follower-count">
            {{ formatFollowerCount(record.blogger.follower_count) }}
          </span>
        </div>

        <!-- 发布时间 -->
        <span class="publish-time">{{ formatTime(record.created_at) }}</span>

        <!-- 互动数据 -->
        <div class="metrics">
          <span class="metric-item likes">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
            </svg>
            {{ formatMetric(record.metrics.likes) }}
          </span>
          <span class="metric-item saves">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path>
            </svg>
            {{ formatMetric(record.metrics.saves) }}
          </span>
          <span class="metric-item comments">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
            </svg>
            {{ formatMetric(record.metrics.comments) }}
          </span>
        </div>

        <!-- 打开原文按钮 -->
        <a
          v-if="record.note_link"
          :href="record.note_link"
          target="_blank"
          rel="noopener noreferrer"
          class="open-link"
          @click.stop
          title="打开原文"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
            <polyline points="15 3 21 3 21 9"></polyline>
            <line x1="10" y1="14" x2="21" y2="3"></line>
          </svg>
        </a>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { ReferenceRecord } from '@/api'

/**
 * 对标文案列表项组件
 *
 * 紧凑的列表布局，单条记录高度约70px
 */

// 定义 Props
const props = defineProps<{
  record: ReferenceRecord
  mode?: 'benchmark' | 'search'
}>()

// 定义 Emits
defineEmits<{
  (e: 'detail', id: string): void
}>()

const isBenchmarkMode = computed(() => props.mode === 'benchmark')

// Type-safe access to mode-specific field
const hasTargetFlag = computed(() => {
  if (isBenchmarkMode.value) {
    // For benchmark mode, check if record has target flag
    // Note: This field comes from Feishu data transformation
    const record = props.record as ReferenceRecord & { is_target_for_creation?: boolean }
    return record.is_target_for_creation === true
  }
  return false
})

/**
 * 格式化粉丝数
 */
function formatFollowerCount(count: number): string {
  if (count >= 10000) {
    return (count / 10000).toFixed(1) + 'w'
  }
  return count.toString()
}

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

/**
 * 格式化时间
 */
function formatTime(dateStr: string | null): string {
  if (!dateStr) return '未知'
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))

  if (days === 0) return '今天'
  if (days === 1) return '昨天'
  if (days < 7) return days + '天前'
  if (days < 30) return Math.floor(days / 7) + '周前'
  if (days < 365) return Math.floor(days / 30) + '月前'
  return Math.floor(days / 365) + '年前'
}
</script>

<style scoped>
/* 桌面宽屏列表项 */
.list-item-card {
  display: flex;
  gap: 16px;
  padding: 16px;
  background: white;
  border-radius: 10px;
  border: 1px solid #e8e6e3;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.list-item-card:hover {
  border-color: #d0cdc9;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
  transform: translateY(-1px);
}

/* 封面图 */
.item-cover {
  width: 72px;
  height: 96px;
  flex-shrink: 0;
  border-radius: 8px;
  overflow: hidden;
  background: #f0efed;
}

.item-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.item-cover.placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ccc;
}

/* 内容区 */
.item-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 10px;
  min-width: 0;
}

/* 标题行 */
.item-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}

.item-title {
  flex: 1;
  font-size: 15px;
  font-weight: 600;
  color: #1a1a1a;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* 徽章 */
.item-badges {
  display: flex;
  gap: 6px;
  flex-shrink: 0;
}

.badge {
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
}

.type-badge {
  background: #f0efed;
  color: #666;
}

.industry-badge {
  background: linear-gradient(135deg, rgba(255, 36, 66, 0.1) 0%, rgba(255, 107, 107, 0.1) 100%);
  color: var(--primary, #ff2442);
}

/* 正文预览 */
.item-preview {
  font-size: 13px;
  color: #666;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* 标签 */
.item-tags {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.inline-tag {
  display: inline-flex;
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
}

.inline-tag.target {
  background: linear-gradient(135deg, rgba(255, 36, 66, 0.1), rgba(255, 107, 107, 0.1));
  color: var(--primary, #ff2442);
}

.tag {
  font-size: 12px;
  color: var(--primary, #ff2442);
}

.tag-more {
  font-size: 12px;
  color: #999;
}

/* 底部信息行 */
.item-footer {
  display: flex;
  align-items: center;
  gap: 16px;
  padding-top: 4px;
}

/* 博主信息 */
.blogger-info {
  display: flex;
  align-items: center;
  gap: 8px;
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
  font-weight: 500;
  color: #333;
  max-width: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.follower-count {
  font-size: 12px;
  color: #999;
}

/* 发布时间 */
.publish-time {
  font-size: 12px;
  color: #999;
}

/* 互动数据 */
.metrics {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-left: auto;
}

.metric-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  font-weight: 500;
}

.metric-item svg {
  color: #ccc;
}

.metric-item.likes {
  color: #ff6b6b;
}

.metric-item.likes svg {
  color: #ff6b6b;
}

.metric-item.saves {
  color: #ffa94d;
}

.metric-item.saves svg {
  color: #ffa94d;
}

.metric-item.comments {
  color: #69b7ff;
}

.metric-item.comments svg {
  color: #69b7ff;
}

/* 打开原文链接 */
.open-link {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 6px;
  color: #999;
  transition: all 0.15s;
  flex-shrink: 0;
}

.open-link:hover {
  background: linear-gradient(135deg, rgba(255, 36, 66, 0.1) 0%, rgba(255, 107, 107, 0.1) 100%);
  color: var(--primary, #ff2442);
}
</style>
