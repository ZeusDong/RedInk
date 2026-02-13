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
      <div v-if="!expanded" class="content-preview markdown-body" v-html="previewHtml"></div>
      <div v-else class="content-full markdown-body" v-html="fullHtml"></div>
    </div>

    <!-- 卡片底部 -->
    <div class="card-footer">
      <button @click="toggleExpanded" class="expand-btn">
        {{ expanded ? '收起全文' : '展开全文' }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
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

// 配置 marked 选项
marked.setOptions({
  gfm: true,
  breaks: true
})

// 渲染 Markdown 并清理 HTML
function renderMarkdown(content: string): string {
  if (!content) return ''
  const html = marked.parse(content) as string
  return DOMPurify.sanitize(html, {
    ALLOWED_TAGS: [
      'p', 'br', 'strong', 'em', 'u', 's', 'code', 'pre',
      'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
      'ul', 'ol', 'li',
      'table', 'thead', 'tbody', 'tr', 'th', 'td',
      'blockquote', 'hr', 'a', 'img', 'span', 'div'
    ],
    ALLOWED_ATTR: [
      'href', 'src', 'alt', 'title', 'class', 'id', 'rowspan', 'colspan'
    ],
    ALLOW_DATA_ATTR: false
  })
}

// 完整内容的 HTML
const fullHtml = computed(() => renderMarkdown(props.summary.content))

// 预览内容的 HTML（截取前 500 字符后再渲染）
const previewHtml = computed(() => {
  const content = props.summary.content
  if (content.length <= 500) return fullHtml.value

  // 智能截取：尽量在段落边界截断
  let truncated = content.substring(0, 500)
  const lastParagraphEnd = truncated.lastIndexOf('\n\n')
  if (lastParagraphEnd > 300) {
    truncated = truncated.substring(0, lastParagraphEnd)
  }

  return renderMarkdown(truncated)
})

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

function toggleExpanded() {
  expanded.value = !expanded.value
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

.content-preview {
  max-height: 300px;
  overflow: hidden;
  position: relative;
}

.content-preview::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 80px;
  background: linear-gradient(to bottom, rgba(255, 255, 255, 0), rgba(255, 255, 255, 1));
  pointer-events: none;
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

/* === Markdown 内容样式 === */
.content-preview,
.content-full {
  line-height: 1.8;
  color: var(--text-main, #1a1a1a);
  font-size: 15px;
  word-wrap: break-word;
}

/* 标题样式 */
.content-preview :deep(h1),
.content-full :deep(h1) {
  font-size: 22px;
  font-weight: 700;
  margin: 24px 0 14px;
  padding-bottom: 6px;
  color: var(--text-main, #1a1a1a);
  border-bottom: 2px solid var(--primary, #ff2442);
}

.content-preview :deep(h2),
.content-full :deep(h2) {
  font-size: 19px;
  font-weight: 600;
  margin: 20px 0 12px;
  padding-bottom: 5px;
  color: var(--text-main, #1a1a1a);
  border-bottom: 1px solid #e8e6e3;
}

.content-preview :deep(h3),
.content-full :deep(h3) {
  font-size: 17px;
  font-weight: 600;
  margin: 18px 0 10px;
  color: var(--text-main, #1a1a1a);
}

.content-preview :deep(h4),
.content-full :deep(h4) {
  font-size: 15px;
  font-weight: 600;
  margin: 14px 0 8px;
  color: var(--text-main, #1a1a1a);
}

/* 段落和行内元素 */
.content-preview :deep(p),
.content-full :deep(p) {
  margin: 8px 0;
}

.content-preview :deep(strong),
.content-full :deep(strong) {
  color: var(--primary, #ff2442);
  font-weight: 600;
}

.content-preview :deep(em),
.content-full :deep(em) {
  font-style: italic;
  color: #555;
}

.content-preview :deep(code),
.content-full :deep(code) {
  background: linear-gradient(135deg, #f8f8f8 0%, #f0f0f0 100%);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'SF Mono', 'Monaco', 'Inconsolata', 'Courier New', monospace;
  font-size: 0.9em;
  color: #e83e8c;
  border: 1px solid #e8e8e8;
}

.content-preview :deep(pre),
.content-full :deep(pre) {
  background: linear-gradient(135deg, #2d2d2d 0%, #1a1a1a 100%);
  padding: 14px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 14px 0;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

.content-preview :deep(pre code),
.content-full :deep(pre code) {
  background: transparent;
  padding: 0;
  border: none;
  color: #f8f8f2;
  font-size: 13px;
}

/* 列表样式 */
.content-preview :deep(ul),
.content-full :deep(ul),
.content-preview :deep(ol),
.content-full :deep(ol) {
  margin: 10px 0;
  padding-left: 22px;
}

.content-preview :deep(li),
.content-full :deep(li) {
  margin: 5px 0;
  line-height: 1.7;
}

.content-preview :deep(li::marker),
.content-full :deep(li::marker) {
  color: var(--primary, #ff2442);
}

/* 表格样式 */
.content-preview :deep(table),
.content-full :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 16px 0;
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
  font-size: 13px;
}

.content-preview :deep(thead),
.content-full :deep(thead) {
  background: linear-gradient(135deg, rgba(255, 36, 66, 0.08) 0%, rgba(255, 107, 107, 0.08) 100%);
}

.content-preview :deep(th),
.content-full :deep(th) {
  padding: 12px 14px;
  text-align: left;
  font-weight: 600;
  color: var(--text-main, #1a1a1a);
  border-bottom: 2px solid var(--primary, #ff2442);
  font-size: 13px;
}

.content-preview :deep(td),
.content-full :deep(td) {
  padding: 10px 14px;
  border-bottom: 1px solid #e8e6e3;
  border-right: 1px solid #f0f0f0;
  vertical-align: top;
  font-size: 13px;
}

.content-preview :deep(tr:last-child td),
.content-full :deep(tr:last-child td) {
  border-bottom: none;
}

.content-preview :deep(tr td:last-child),
.content-full :deep(tr td:last-child) {
  border-right: none;
}

.content-preview :deep(tr:hover),
.content-full :deep(tr:hover) {
  background: #fafafa;
}

/* 引用块样式 */
.content-preview :deep(blockquote),
.content-full :deep(blockquote) {
  margin: 14px 0;
  padding: 10px 16px;
  border-left: 4px solid var(--primary, #ff2442);
  background: linear-gradient(90deg, rgba(255, 36, 66, 0.05) 0%, rgba(255, 107, 107, 0.02) 100%);
  color: #555;
  font-style: italic;
  border-radius: 0 6px 6px 0;
  font-size: 14px;
}

/* 分隔线样式 */
.content-preview :deep(hr),
.content-full :deep(hr) {
  border: none;
  height: 2px;
  background: linear-gradient(90deg, transparent 0%, #e8e6e3 50%, transparent 100%);
  margin: 20px 0;
}

/* 链接样式 */
.content-preview :deep(a),
.content-full :deep(a) {
  color: var(--primary, #ff2442);
  text-decoration: none;
  border-bottom: 1px dashed var(--primary, #ff2442);
  transition: all 0.2s;
}

.content-preview :deep(a:hover),
.content-full :deep(a:hover) {
  background: rgba(255, 36, 66, 0.1);
  border-bottom-style: solid;
}

/* 图片样式 */
.content-preview :deep(img),
.content-full :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
  margin: 10px 0;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}
</style>
