<template>
  <div class="optimizer-panel">
    <!-- 内容输入区 -->
    <div v-if="!optimizerStore.currentContent" class="content-input">
      <div class="input-header">
        <h3>✨ 内容优化助手</h3>
        <p class="subtitle">粘贴或上传你想要优化的内容</p>
      </div>

      <div class="input-tabs">
        <button
          @click="inputMode = 'paste'"
          :class="{ active: inputMode === 'paste' }"
          class="tab-btn"
        >
          粘贴内容
        </button>
        <button
          @click="handleImport"
          :class="{ active: inputMode === 'import' }"
          class="tab-btn"
        >
          导入生成结果
        </button>
      </div>

      <div v-if="inputMode === 'paste'" class="paste-area">
        <textarea
          v-model="pastedContent"
          placeholder="粘贴你的标题、大纲或正文内容..."
          class="content-textarea"
        ></textarea>
        <button
          @click="handleAnalyze"
          :disabled="!pastedContent.trim()"
          class="analyze-btn"
        >
          开始分析
        </button>
      </div>

      <div v-else class="import-area">
        <p class="import-tip">从历史记录中导入最近一次生成的内容</p>
        <button @click="handleImport" class="import-btn">
          导入最近生成
        </button>
      </div>
    </div>

    <!-- 分析结果区 -->
    <div v-else class="analysis-result">
      <!-- 评分显示 -->
      <ScoreDisplay
        :score="optimizerStore.score"
        :improvement="improvementPotential"
      />

      <!-- 建议列表 -->
      <div class="suggestions-section">
        <div class="section-header">
          <h4>💡 优化建议 ({{ pendingSuggestions.length }})</h4>
          <button
            v-if="pendingSuggestions.length > 0"
            @click="handleApplyAll"
            class="apply-all-btn"
          >
            全部应用
          </button>
        </div>

        <div v-if="pendingSuggestions.length === 0" class="empty-suggestions">
          <div class="empty-icon">✅</div>
          <p>太棒了！没有需要优化的地方</p>
        </div>

        <div v-else class="suggestions-list">
          <SuggestionCard
            v-for="suggestion in pendingSuggestions"
            :key="suggestion.id"
            :suggestion="suggestion"
            @apply="handleApplySuggestion"
            @dismiss="handleDismissSuggestion"
            @view-reference="handleViewReference"
          />
        </div>
      </div>

      <!-- 优化后内容预览 -->
      <div class="optimized-content">
        <div class="section-header">
          <h4>📄 优化后内容</h4>
          <div class="actions">
            <button @click="handleCopy" class="action-btn">复制</button>
            <button @click="handleReset" class="action-btn secondary">重新分析</button>
          </div>
        </div>
        <div class="content-preview">
          <h5 v-if="optimizerStore.currentContent?.title" class="preview-title">
            {{ optimizerStore.currentContent.title }}
          </h5>
          <div v-if="optimizerStore.currentContent?.body" class="preview-body">
            {{ optimizerStore.currentContent.body }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useOptimizerStore } from '@/stores/optimizer'
import type { Suggestion } from '@/stores/optimizer'
import ScoreDisplay from './ScoreDisplay.vue'
import SuggestionCard from './SuggestionCard.vue'

const optimizerStore = useOptimizerStore()
const inputMode = ref<'paste' | 'import'>('paste')
const pastedContent = ref('')

const pendingSuggestions = computed(() => {
  return optimizerStore.suggestions.filter(s => !s.applied)
})

const improvementPotential = computed(() => {
  const appliedCount = optimizerStore.suggestions.filter(s => s.applied).length
  const totalImprovable = optimizerStore.suggestions.length
  if (totalImprovable === 0) return 0
  return Math.round((appliedCount / totalImprovable) * 100)
})

async function handleAnalyze() {
  if (!pastedContent.value.trim()) return

  try {
    const response = await fetch('/api/optimize/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        content: {
          body: pastedContent.value
        }
      })
    })

    const data = await response.json()
    if (data.success) {
      optimizerStore.currentContent = { body: pastedContent.value }
      optimizerStore.score = data.data.score
      optimizerStore.suggestions = data.data.suggestions || []
    } else {
      console.error('分析失败:', data.error)
      alert('内容分析失败: ' + (data.error || '未知错误'))
    }
  } catch (error) {
    console.error('分析异常:', error)
    alert('内容分析失败，请稍后重试')
  }
}

async function handleImport() {
  // TODO: Import from generator store
  console.log('Importing from generator store...')
}

async function handleApplySuggestion(suggestion: Suggestion) {
  try {
    const response = await fetch('/api/optimize/apply', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        suggestion_id: suggestion.id,
        action_type: suggestion.action_type,
        action_data: suggestion.action_data
      })
    })

    const data = await response.json()
    if (data.success) {
      suggestion.applied = true
      if (data.data.updated_content) {
        optimizerStore.currentContent = data.data.updated_content
      }
      if (data.data.new_score) {
        optimizerStore.score = data.data.new_score
      }
    }
  } catch (error) {
    console.error('应用建议失败:', error)
  }
}

async function handleDismissSuggestion(suggestion: Suggestion) {
  try {
    const response = await fetch('/api/optimize/dismiss', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        suggestion_id: suggestion.id
      })
    })

    const data = await response.json()
    if (data.success) {
      suggestion.applied = true
    }
  } catch (error) {
    console.error('忽略建议失败:', error)
  }
}

async function handleApplyAll() {
  for (const suggestion of optimizerStore.suggestions) {
    if (suggestion.severity === 'critical' || suggestion.severity === 'warning') {
      await handleApplySuggestion(suggestion)
    }
  }
}

function handleViewReference(record: any) {
  console.log('View reference:', record)
}

function handleCopy() {
  const content = optimizerStore.currentContent
  if (!content) return

  const text = [
    content.title || '',
    content.body || ''
  ].filter(Boolean).join('\n\n')

  navigator.clipboard.writeText(text)
  // TODO: Show toast notification
}

function handleReset() {
  optimizerStore.reset()
  pastedContent.value = ''
  inputMode.value = 'paste'
}
</script>

<style scoped>
.optimizer-panel {
  max-width: 900px;
  margin: 0 auto;
}

.content-input {
  background: white;
  border-radius: 12px;
  padding: 24px;
}

.input-header {
  text-align: center;
  margin-bottom: 24px;
}

.input-header h3 {
  font-size: 22px;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0 0 8px 0;
}

.subtitle {
  font-size: 14px;
  color: #666;
  margin: 0;
}

.input-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
  padding: 4px;
  background: #f8f7f5;
  border-radius: 8px;
}

.tab-btn {
  flex: 1;
  padding: 10px;
  border: none;
  background: transparent;
  color: #666;
  font-size: 14px;
  font-weight: 500;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.tab-btn.active {
  background: white;
  color: var(--primary, #ff2442);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.paste-area {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.content-textarea {
  min-height: 200px;
  width: 100%;
  padding: 12px;
  border: 1px solid #e0dedb;
  border-radius: 8px;
  font-size: 14px;
  resize: vertical;
  font-family: inherit;
}

.content-textarea:focus {
  outline: none;
  border-color: var(--primary, #ff2442);
}

.analyze-btn {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  background: var(--primary, #ff2442);
  color: white;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.analyze-btn:hover:not(:disabled) {
  background: #e61f37;
}

.analyze-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.import-area {
  text-align: center;
}

.import-tip {
  font-size: 13px;
  color: #666;
  margin-bottom: 12px;
}

.import-btn {
  padding: 10px 24px;
  border: 1px solid #e0dedb;
  border-radius: 8px;
  background: white;
  color: #333;
  font-size: 14px;
  cursor: pointer;
}

.import-btn:hover {
  border-color: var(--primary, #ff2442);
  color: var(--primary, #ff2442);
}

.analysis-result {
  background: white;
  border-radius: 12px;
  padding: 24px;
}

.suggestions-section {
  margin-top: 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-header h4 {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.apply-all-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 8px;
  background: var(--primary, #ff2442);
  color: white;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
}

.apply-all-btn:hover {
  background: #e61f37;
}

.empty-suggestions {
  text-align: center;
  padding: 40px;
}

.empty-suggestions .empty-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.empty-suggestions p {
  font-size: 14px;
  color: #666;
  margin: 0;
}

.suggestions-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.optimized-content {
  margin-top: 24px;
  padding: 16px;
  background: #f8f7f5;
  border-radius: 8px;
}

.actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  padding: 8px 16px;
  border: 1px solid #e0dedb;
  border-radius: 6px;
  background: white;
  color: #333;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn:hover {
  border-color: #666;
}

.action-btn.secondary {
  border-color: #e0dedb;
}

.content-preview {
  margin-top: 12px;
}

.preview-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin: 0 0 8px 0;
}

.preview-body {
  font-size: 14px;
  color: #666;
  line-height: 1.6;
}
</style>
