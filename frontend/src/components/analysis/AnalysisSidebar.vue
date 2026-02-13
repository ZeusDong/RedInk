<template>
  <Transition name="slide">
    <aside v-if="store.sidebarExpanded || store.selectedRecord" class="analysis-sidebar">
      <!-- 头部 -->
      <header class="sidebar-header">
        <h2 class="sidebar-title">📋 分析结果</h2>
        <button class="close-btn" @click="handleClose" title="关闭">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </header>

      <!-- 内容区 -->
      <div class="sidebar-content">
        <!-- 未选择笔记 -->
        <div v-if="!store.selectedRecord" class="empty-state">
          <div class="empty-icon">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5.586a1 1 0 0 1 .707.293l5.414 5.414a1 1 0 0 1 .293.707V19a2 2 0 0 1-2 2Z"></path>
            </svg>
          </div>
          <p>点击笔记卡片查看分析结果</p>
        </div>

        <!-- 已选择笔记，但未分析 -->
        <div v-else-if="!store.isAnalyzed" class="pending-state">
          <div class="record-preview">
            <div v-if="store.selectedRecord.cover_image" class="preview-cover">
              <img :src="store.selectedRecord.cover_image" alt="" />
            </div>
            <div class="preview-info">
              <h3 class="preview-title">{{ store.selectedRecord.title }}</h3>
              <div class="preview-metrics">
                <span v-if="store.selectedRecord.metrics" class="metric">
                  👍 {{ formatCount(store.selectedRecord.metrics.likes) }}
                </span>
                <span v-if="store.selectedRecord.metrics" class="metric">
                  💾 {{ formatCount(store.selectedRecord.metrics.saves) }}
                </span>
              </div>
            </div>
          </div>

          <div class="action-area">
            <p class="hint">该笔记尚未进行分析</p>
            <button class="analyze-btn" @click="openConfirmModal" :disabled="store.loading">
              <svg v-if="!store.loading" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 12a9 9 0 1 1-6.219-8.56"></path>
              </svg>
              <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="spin">
                <path d="M21 12a9 9 0 1 1-6.219-8.56"></path>
              </svg>
              {{ store.loading ? '分析中...' : '开始 AI 分析' }}
            </button>
          </div>
        </div>

        <!-- 已分析 -->
        <div v-else class="analyzed-state">
          <div class="record-preview compact">
            <h3 class="preview-title">{{ store.selectedRecord?.title }}</h3>
          </div>

          <!-- Markdown 渲染的内容 -->
          <div class="analysis-content" v-html="renderedContent"></div>

          <!-- 重新分析按钮 -->
          <div class="reanalyze-action">
            <button class="reanalyze-btn" @click="handleReanalyze">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M23 4v6h-6"></path>
                <path d="M1 20v-6h6"></path>
                <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
              </svg>
              重新分析
            </button>
          </div>
        </div>
      </div>
    </aside>
  </Transition>

  <!-- AI分析确认弹窗 -->
  <AnalyzeConfirmModal
    :visible="confirmModalVisible"
    :record="store.selectedRecord"
    @close="closeConfirmModal"
    @save-draft="handleSaveDraft"
    @submit="handleSubmit"
  />
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import { useAnalysisStore } from '@/stores/analysis'
import AnalyzeConfirmModal from './AnalyzeConfirmModal.vue'

const store = useAnalysisStore()

// 确认弹窗状态
const confirmModalVisible = ref(false)

// 渲染 Markdown 内容
const renderedContent = computed(() => {
  if (!store.selectedRecord) return ''

  const result = store.analysisResults.get(store.selectedRecord.record_id)
  if (!result?.content) return ''

  // 配置 marked 选项
  marked.setOptions({
    breaks: true, // 支持换行
    gfm: true, // GitHub Flavored Markdown
  })

  // 解析 Markdown 并净化 HTML
  const rawHtml = marked(result.content) as string
  return DOMPurify.sanitize(rawHtml)
})

// 格式化数字
function formatCount(count: number): string {
  if (count >= 10000) return (count / 10000).toFixed(1) + 'w'
  if (count >= 1000) return (count / 1000).toFixed(1) + 'k'
  return count.toString()
}

// 关闭侧边栏
function handleClose() {
  store.closeSidebar()
  store.clearSelection()
}

// 打开确认弹窗
function openConfirmModal() {
  confirmModalVisible.value = true
}

// 关闭确认弹窗
function closeConfirmModal() {
  confirmModalVisible.value = false
}

// 保存草稿
function handleSaveDraft(data: any) {
  console.log('草稿已保存:', data)
  // TODO: 可以添加 toast 提示
}

// 提交分析
function handleSubmit(data: any) {
  console.log('分析已提交:', data)
  // TODO: 可以添加 toast 提示，并轮询分析结果
}

// 重新分析
function handleReanalyze() {
  openConfirmModal()
}
</script>

<style scoped>
/* 侧边栏容器 */
.analysis-sidebar {
  position: fixed;
  top: 64px; /* header height */
  right: 0;
  width: 400px;
  height: calc(100vh - 64px);
  background: white;
  border-left: 1px solid #e8e6e3;
  box-shadow: -4px 0 16px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  z-index: 101;
}

/* 滑入动画 */
.slide-enter-active,
.slide-leave-active {
  transition: transform 0.3s ease, opacity 0.3s ease;
}

.slide-enter-from,
.slide-leave-to {
  transform: translateX(100%);
  opacity: 0;
}

/* 头部 */
.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e8e6e3;
}

.sidebar-title {
  font-size: 16px;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0;
}

.close-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  color: #999;
  cursor: pointer;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.close-btn:hover {
  background: #f8f7f5;
  color: #666;
}

/* 内容区 */
.sidebar-content {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
  color: #999;
}

.empty-icon {
  width: 64px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8f7f5;
  border-radius: 50%;
  margin-bottom: 20px;
  color: #ccc;
}

.empty-state p {
  font-size: 14px;
  line-height: 1.6;
}

/* 待分析状态 */
.pending-state {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.record-preview {
  display: flex;
  gap: 16px;
  padding: 16px;
  background: #f8f7f5;
  border-radius: 12px;
}

.preview-cover {
  width: 80px;
  height: 80px;
  flex-shrink: 0;
  border-radius: 8px;
  overflow: hidden;
  background: #eee;
}

.preview-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.preview-info {
  flex: 1;
  min-width: 0;
}

.preview-title {
  font-size: 14px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0 0 12px 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.preview-metrics {
  display: flex;
  gap: 12px;
}

.metric {
  font-size: 12px;
  color: #666;
}

/* 操作区域 */
.action-area {
  text-align: center;
}

.hint {
  font-size: 13px;
  color: #999;
  margin: 0 0 16px 0;
}

.analyze-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 24px;
  border-radius: 8px;
  border: none;
  background: var(--primary, #ff2442);
  color: white;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  width: 100%;
}

.analyze-btn:hover:not(:disabled) {
  background: #e61e3a;
}

.analyze-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.analyze-btn svg.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 已分析状态 */
.analyzed-state {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.record-preview.compact {
  padding: 12px;
}

.record-preview.compact .preview-title {
  margin-bottom: 0;
}

.analysis-content {
  padding: 20px;
  background: #f8f7f5;
  border-radius: 12px;
  line-height: 1.7;
  font-size: 14px;
  color: #333;
  overflow-x: auto;
}

/* Markdown Content Styles */
.analysis-content :deep(h1),
.analysis-content :deep(h2),
.analysis-content :deep(h3),
.analysis-content :deep(h4),
.analysis-content :deep(h5),
.analysis-content :deep(h6) {
  margin-top: 24px;
  margin-bottom: 16px;
  font-weight: 700;
  color: #1a1a1a;
}

.analysis-content :deep(h1) { font-size: 20px; }
.analysis-content :deep(h2) { font-size: 18px; }
.analysis-content :deep(h3) { font-size: 16px; }
.analysis-content :deep(h4) { font-size: 15px; }

.analysis-content :deep(p) {
  margin-bottom: 12px;
  line-height: 1.7;
}

.analysis-content :deep(ul),
.analysis-content :deep(ol) {
  margin-bottom: 16px;
  padding-left: 24px;
}

.analysis-content :deep(li) {
  margin-bottom: 8px;
}

.analysis-content :deep(code) {
  background: #e8e6e3;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 13px;
  color: #e61e3a;
}

.analysis-content :deep(pre) {
  background: #f0efed;
  padding: 16px;
  border-radius: 8px;
  overflow-x: auto;
  margin-bottom: 16px;
}

.analysis-content :deep(pre code) {
  background: transparent;
  padding: 0;
  color: #333;
}

.analysis-content :deep(blockquote) {
  border-left: 4px solid var(--primary, #ff2442);
  padding-left: 16px;
  margin: 16px 0;
  color: #666;
  font-style: italic;
}

.analysis-content :deep(a) {
  color: var(--primary, #ff2442);
  text-decoration: none;
}

.analysis-content :deep(a:hover) {
  text-decoration: underline;
}

.analysis-content :deep(strong) {
  font-weight: 700;
  color: #1a1a1a;
}

.analysis-content :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 16px;
}

.analysis-content :deep(th),
.analysis-content :deep(td) {
  padding: 12px;
  border: 1px solid #e8e6e3;
  text-align: left;
}

.analysis-content :deep(th) {
  background: #f8f7f5;
  font-weight: 600;
}

.analysis-content :deep(hr) {
  border: none;
  border-top: 1px solid #e8e6e3;
  margin: 24px 0;
}

/* 重新分析操作 */
.reanalyze-action {
  padding-top: 16px;
  border-top: 1px solid #e8e6e3;
}

.reanalyze-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  padding: 12px 20px;
  border: 1px solid #e0dedb;
  border-radius: 10px;
  background: white;
  color: #666;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.reanalyze-btn:hover {
  border-color: var(--primary, #ff2442);
  color: var(--primary, #ff2442);
  background: linear-gradient(135deg, rgba(255, 36, 66, 0.08) 0%, rgba(255, 107, 107, 0.08) 100%);
}

.reanalyze-btn svg {
  transition: transform 0.3s ease;
}

.reanalyze-btn:hover svg {
  transform: rotate(180deg);
}

.placeholder {
  font-size: 14px;
  color: #666;
  margin: 0 0 8px 0;
}

.note {
  font-size: 12px;
  color: #999;
  margin: 0;
}
</style>
