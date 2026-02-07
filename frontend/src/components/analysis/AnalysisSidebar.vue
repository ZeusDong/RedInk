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
          <p>点击笔记卡片上的「对标分析」按钮<br>查看分析结果</p>
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
            <button class="analyze-btn" @click="handleAnalyze" :disabled="store.loading">
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

          <div class="analysis-content">
            <p class="placeholder">分析结果将在这里显示...</p>
            <p class="note">（后续版本实现）</p>
          </div>
        </div>
      </div>
    </aside>
  </Transition>
</template>

<script setup lang="ts">
import { useAnalysisStore } from '@/stores/analysis'

const store = useAnalysisStore()

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

// 开始分析（占位）
function handleAnalyze() {
  // 后续实现
  console.log('开始分析:', store.selectedRecord?.record_id)
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
  z-index: 50;
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
