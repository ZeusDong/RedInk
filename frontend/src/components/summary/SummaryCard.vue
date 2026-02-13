<template>
  <div class="summary-card">
    <!-- 卡片头部 -->
    <div class="card-header">
      <div class="header-info">
        <h3 class="industry-name">{{ summary.industry }}</h3>
        <span class="record-count">{{ summary.record_count }} 条笔记</span>
        <span class="date">{{ formatDate(summary.created_at) }}</span>
      </div>
      <div class="header-actions">
        <button
          @click="$emit('delete', summary.id)"
          class="delete-btn"
          title="删除总结"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M3 6h18" />
            <path d="M19 6v14a2 2 0 0 1-2-2h-10a2 2 0 0 1 2 2v14a2 2 0 0 1 2 2z" />
          </svg>
        </button>
      </div>
    </div>

    <!-- 总结内容 -->
    <div class="card-content">
      <div v-if="!expanded" class="content-preview">
        <div v-html="getPreview(summary.content)"></div>
      </div>
      <div v-else class="content-full">
        <div v-html="summary.content"></div>
      </div>
    </div>

    <!-- 卡片底部 -->
    <div class="card-footer" v-if="!expanded">
      <button @click="expand" class="expand-btn">
        展开全文
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { Summary } from '@/api/summary'

/**
 * AI总结卡片组件
 *
 * 显示AI生成的总结内容，支持展开/收起
 */
const props = defineProps<{
  summary: Summary
}>()

const emit = defineEmits<{
  (e: 'delete', id: number): void
}>()

const expanded = ref(false)

// 预览总结内容（截取前200字符）
const getPreview = (content: string): string => {
  if (content.length <= 200) return content
  return content.substring(0, 200) + '...'
}

// 格式化日期
function formatDate(dateString: string): string {
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

  if (diffDays === 0) return '今天'
  if (diffDays === 1) return '昨天'
  if (diffDays < 7) return `${diffDays} 天前`
  if (diffDays < 30) return `${Math.floor(diffDays / 7)} 周前`
  return dateString.substring(0, 10)
}

function expand() {
  expanded.value = true
}
</script>

<style scoped>
.summary-card {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  border: 2px solid transparent;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.summary-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.08);
}

/* 卡片头部 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: linear-gradient(135deg, rgba(255, 36, 66, 0.05) 0%, rgba(255, 107, 107, 0.05) 100%);
  border-bottom: 1px solid #e8e6e3;
}

.header-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.industry-name {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-main, #1a1a1a);
}

.record-count {
  font-size: 13px;
  color: var(--text-sub, #666);
  padding: 4px 12px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 6px;
}

.date {
  font-size: 13px;
  color: var(--text-placeholder, #999);
}

.header-actions {
  display: flex;
  gap: 8px;
}

.delete-btn {
  padding: 8px;
  border: none;
  background: transparent;
  cursor: pointer;
  border-radius: 8px;
  transition: all 0.2s;
  color: var(--text-sub, #666);
}

.delete-btn:hover {
  background: #fee;
  color: #d32f2f;
}

/* 卡片内容 */
.card-content {
  padding: 20px;
}

.content-preview,
.content-full {
  line-height: 1.8;
  color: var(--text-main, #1a1a1a);
}

.content-preview {
  max-height: 200px;
  overflow: hidden;
  position: relative;
}

.content-preview::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 60px;
  background: linear-gradient(to bottom, rgba(255, 255, 255, 0), rgba(255, 255, 255, 1));
}

/* 卡片底部 */
.card-footer {
  padding: 12px 20px;
  border-top: 1px solid #e8e6e3;
  background: #fafafa;
}

.expand-btn {
  width: 100%;
  padding: 10px;
  border: none;
  background: transparent;
  cursor: pointer;
  font-size: 14px;
  color: var(--primary, #ff2442);
  transition: all 0.2s;
}

.expand-btn:hover {
  background: #f0efed;
}

/* 内容样式覆盖 */
.content-full :deep(h1),
.content-full :deep(h2),
.content-full :deep(h3),
.content-full :deep(h4),
.content-preview :deep(h1),
.content-preview :deep(h2),
.content-preview :deep(h3),
.content-preview :deep(h4) {
  margin-top: 16px;
  margin-bottom: 12px;
  color: var(--text-main, #1a1a1a);
}

.content-full :deep(ul),
.content-preview :deep(ul),
.content-full :deep(ol),
.content-preview :deep(ol) {
  margin: 12px 0;
  padding-left: 24px;
}

.content-full :deep(li),
.content-preview :deep(li) {
  margin-bottom: 8px;
}

.content-full :deep(table),
.content-preview :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 16px 0;
}

.content-full :deep(th),
.content-full :deep(td) {
  padding: 10px 12px;
  border: 1px solid #e8e6e3;
  text-align: left;
}

.content-full :strong {
  color: var(--primary, #ff2442);
  font-weight: 600;
}
</style>
