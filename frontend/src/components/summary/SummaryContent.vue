<template>
  <div class="summary-content" v-html="renderedContent"></div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

/**
 * AI总结内容展示组件
 *
 * 渲染AI生成的总结内容，支持Markdown格式
 */
const props = defineProps<{
  content: string
}>()

// 简单的Markdown渲染（处理标题、列表、表格等）
const renderedContent = computed(() => {
  let html = props.content

  // 转义HTML
  html = html
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')

  // 处理标题 (## 标题)
  html = html.replace(/^##\s+(.+)$/gm, '<h3>$1</h3>')
  html = html.replace(/^#\s+(.+)$/gm, '<h2>$1</h2>')
  html = html.replace(/^####\s+(.+)$/gm, '<h4>$1</h4>')

  // 处理粗体 (**文本**)
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')

  // 处理列表项
  html = html.replace(/^-\s+(.+)$/gm, '<li>$1</li>')

  // 处理表格 (简化处理，实际应该使用markdown库）
  html = html.replace(/\|(.+)\|/g, (match, p1) => {
    if (match.includes('---')) return match // 表格分隔线
    const cells = p1.split('|').filter(c => c.trim())
    const cellHtml = cells.map(c => `<td>${c}</td>`).join('')
    return `<tr>${cellHtml}</tr>`
  })

  // 处理换行
  html = html.replace(/\n\n/g, '</p><p>')
  html = html.replace(/\n/g, '<br>')

  return html
})
</script>

<style scoped>
.summary-content {
  color: var(--text-main, #1a1a1a);
  line-height: 1.8;
}

.summary-content :deep(h3) {
  font-size: 20px;
  font-weight: 600;
  margin: 24px 0 16px;
  color: var(--text-main, #1a1a1a);
}

.summary-content :deep(h2) {
  font-size: 18px;
  font-weight: 600;
  margin: 20px 0 12px;
  color: var(--text-main, #1a1a1a);
}

.summary-content :deep(h4) {
  font-size: 16px;
  font-weight: 600;
  margin: 16px 0 8px;
  color: var(--text-main, #1a1a1a);
}

.summary-content :deep(strong) {
  color: var(--primary, #ff2442);
  font-weight: 600;
}

.summary-content :deep(p) {
  margin: 8px 0;
}

.summary-content :deep(li) {
  margin-left: 24px;
  line-height: 1.8;
}

.summary-content :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 16px 0;
  background: white;
}

.summary-content :deep(tr) {
  border-bottom: 1px solid #e8e6e3;
}

.summary-content :deep(td) {
  padding: 12px 16px;
  text-align: left;
  border-left: 1px solid #e8e6e3;
}

.summary-content :deep(code) {
  background: #f5f5f5;
  padding: 16px;
  border-radius: 8px;
  font-family: 'Courier New', Courier, monospace;
  font-size: 14px;
  overflow-x: auto;
}

.summary-content :deep(pre) {
  background: #f5f5f5;
  padding: 16px;
  border-radius: 8px;
  overflow-x: auto;
  font-family: 'Courier New', Courier, monospace;
  font-size: 13px;
}
</style>
