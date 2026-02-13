<template>
  <div class="summary-content markdown-body" v-html="sanitizedHtml"></div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'

/**
 * AI总结内容展示组件
 *
 * 渲染AI生成的总结内容，使用 marked 解析 Markdown 格式
 * 使用 DOMPurify 清理 HTML 以确保安全性
 */
const props = defineProps<{
  content: string
}>()

// 配置 marked 选项
marked.setOptions({
  gfm: true, // GitHub Flavored Markdown
  breaks: true // 支持换行符
})

// 解析 Markdown 并清理 HTML
const renderedHtml = computed(() => {
  if (!props.content) return ''
  return marked.parse(props.content) as string
})

// 使用 DOMPurify 清理 HTML，只允许安全的标签和属性
const sanitizedHtml = computed(() => {
  return DOMPurify.sanitize(renderedHtml.value, {
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
})
</script>

<style scoped>
.summary-content {
  color: var(--text-main, #1a1a1a);
  line-height: 1.8;
  font-size: 15px;
  word-wrap: break-word;
}

/* === 标题样式 === */
.summary-content :deep(h1) {
  font-size: 24px;
  font-weight: 700;
  margin: 28px 0 16px;
  padding-bottom: 8px;
  color: var(--text-main, #1a1a1a);
  border-bottom: 2px solid var(--primary, #ff2442);
}

.summary-content :deep(h2) {
  font-size: 20px;
  font-weight: 600;
  margin: 24px 0 14px;
  padding-bottom: 6px;
  color: var(--text-main, #1a1a1a);
  border-bottom: 1px solid #e8e6e3;
}

.summary-content :deep(h3) {
  font-size: 18px;
  font-weight: 600;
  margin: 20px 0 12px;
  color: var(--text-main, #1a1a1a);
}

.summary-content :deep(h4) {
  font-size: 16px;
  font-weight: 600;
  margin: 16px 0 10px;
  color: var(--text-main, #1a1a1a);
}

.summary-content :deep(h5),
.summary-content :deep(h6) {
  font-size: 15px;
  font-weight: 600;
  margin: 14px 0 8px;
  color: var(--text-main, #1a1a1a);
}

/* === 段落和行内元素 === */
.summary-content :deep(p) {
  margin: 10px 0;
}

.summary-content :deep(strong) {
  color: var(--primary, #ff2442);
  font-weight: 600;
}

.summary-content :deep(em) {
  font-style: italic;
  color: #555;
}

.summary-content :deep(code) {
  background: linear-gradient(135deg, #f8f8f8 0%, #f0f0f0 100%);
  padding: 3px 8px;
  border-radius: 4px;
  font-family: 'SF Mono', 'Monaco', 'Inconsolata', 'Courier New', monospace;
  font-size: 0.9em;
  color: #e83e8c;
  border: 1px solid #e8e8e8;
}

.summary-content :deep(pre) {
  background: linear-gradient(135deg, #2d2d2d 0%, #1a1a1a 100%);
  padding: 16px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 16px 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.summary-content :deep(pre code) {
  background: transparent;
  padding: 0;
  border: none;
  color: #f8f8f2;
  font-size: 14px;
}

/* === 列表样式 === */
.summary-content :deep(ul),
.summary-content :deep(ol) {
  margin: 12px 0;
  padding-left: 24px;
}

.summary-content :deep(li) {
  margin: 6px 0;
  line-height: 1.8;
}

.summary-content :deep(li::marker) {
  color: var(--primary, #ff2442);
}

/* === 表格样式 === */
.summary-content :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 20px 0;
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.summary-content :deep(thead) {
  background: linear-gradient(135deg, rgba(255, 36, 66, 0.08) 0%, rgba(255, 107, 107, 0.08) 100%);
}

.summary-content :deep(th) {
  padding: 14px 16px;
  text-align: left;
  font-weight: 600;
  color: var(--text-main, #1a1a1a);
  border-bottom: 2px solid var(--primary, #ff2442);
  font-size: 14px;
}

.summary-content :deep(td) {
  padding: 12px 16px;
  border-bottom: 1px solid #e8e6e3;
  border-right: 1px solid #f0f0f0;
  vertical-align: top;
  font-size: 14px;
}

.summary-content :deep(tr:last-child td) {
  border-bottom: none;
}

.summary-content :deep(tr:last-child td:last-child),
.summary-content :deep(tr td:last-child) {
  border-right: none;
}

.summary-content :deep(tr:hover) {
  background: #fafafa;
}

/* === 引用块样式 === */
.summary-content :deep(blockquote) {
  margin: 16px 0;
  padding: 12px 20px;
  border-left: 4px solid var(--primary, #ff2442);
  background: linear-gradient(90deg, rgba(255, 36, 66, 0.05) 0%, rgba(255, 107, 107, 0.02) 100%);
  color: #555;
  font-style: italic;
  border-radius: 0 8px 8px 0;
}

/* === 分隔线样式 === */
.summary-content :deep(hr) {
  border: none;
  height: 2px;
  background: linear-gradient(90deg, transparent 0%, #e8e6e3 50%, transparent 100%);
  margin: 24px 0;
}

/* === 链接样式 === */
.summary-content :deep(a) {
  color: var(--primary, #ff2442);
  text-decoration: none;
  border-bottom: 1px dashed var(--primary, #ff2442);
  transition: all 0.2s;
}

.summary-content :deep(a:hover) {
  background: rgba(255, 36, 66, 0.1);
  border-bottom-style: solid;
}

/* === 图片样式 === */
.summary-content :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
  margin: 12px 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
</style>
