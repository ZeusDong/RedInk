<template>
  <Teleport to="body">
    <Transition name="modal-fade">
      <div v-if="visible" class="modal-overlay" @click.self="handleClose">
        <div class="modal-content">
          <!-- Header -->
          <div class="modal-header">
            <div class="header-title">
              <span class="icon">📋</span>
              <h3>保存为创作技巧</h3>
            </div>
            <button @click="handleClose" class="close-btn" aria-label="关闭">
              ×
            </button>
          </div>

          <!-- Body -->
          <div class="modal-body">
            <!-- Record Preview -->
            <div class="record-preview" v-if="record">
              <div class="preview-cover" v-if="record.cover_url || record.cover_image">
                <img
                  :src="record.cover_url || record.cover_image"
                  :alt="record.title"
                  @error="coverError = true"
                />
              </div>
              <div class="preview-info">
                <h4 class="preview-title">{{ record.title }}</h4>
                <span class="preview-industry">{{ record.industry || '未分类' }}</span>
              </div>
            </div>

            <!-- Loading State -->
            <div v-if="loading" class="loading-section">
              <div class="skeleton-loader">
                <div class="skeleton-header"></div>
                <div class="skeleton-item"></div>
                <div class="skeleton-item"></div>
                <div class="skeleton-item"></div>
                <div class="skeleton-item"></div>
              </div>
              <p class="loading-text">AI 正在分析笔记并提取创作技巧...</p>
            </div>

            <!-- Error State -->
            <div v-else-if="error && !extractedData" class="error-section">
              <div class="error-icon">⚠️</div>
              <p class="error-text">{{ error }}</p>
              <button @click="handleRetry" class="retry-btn">
                重试
              </button>
            </div>

            <!-- Extracted Content -->
            <div v-else-if="extractedData" class="extracted-section">
              <!-- Extracted Elements -->
              <div class="elements-card" :class="{ collapsed: elementsCollapsed }">
                <div class="elements-header">
                  <span class="elements-icon">✨</span>
                  <span class="elements-title">AI 已提取以下创作技巧</span>
                </div>

                <Transition name="collapse">
                  <div v-show="!elementsCollapsed" class="elements-list">
                    <label
                      v-for="element in extractedData.elements"
                      :key="element.type"
                      class="element-item"
                    >
                      <input
                        type="checkbox"
                        v-model="element.selected"
                        class="element-checkbox"
                      />
                      <div class="element-content">
                        <span class="element-type">{{ getElementIcon(element.type) }} {{ element.name }}</span>
                        <span class="element-desc">{{ element.description }}</span>
                      </div>
                    </label>
                  </div>
                </Transition>

                <button @click="elementsCollapsed = !elementsCollapsed" class="toggle-btn">
                  {{ elementsCollapsed ? '展开' : '收起' }}
                  <span class="toggle-arrow">{{ elementsCollapsed ? '▼' : '▲' }}</span>
                </button>
              </div>

              <!-- Hint -->
              <div class="hint-section">
                <span class="hint-icon">💡</span>
                <span class="hint-text">这些技巧将按原笔记分组保存到模板库，方便以后参考学习</span>
              </div>
            </div>
          </div>

          <!-- Footer -->
          <div class="modal-footer">
            <div class="footer-hint" v-if="showSaveHint">
              <span class="hint-icon">⚠️</span>
              <span class="hint-text">{{ saveHintText }}</span>
            </div>
            <div class="footer-buttons">
              <button @click="handleClose" class="footer-btn secondary" :disabled="saving">
                取消
              </button>
              <button
                @click="handleSave"
                class="footer-btn primary"
                :disabled="!isSaveEnabled || saving"
              >
                {{ saving ? '保存中...' : '保存技巧' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useTemplateGroupStore } from '@/stores/templateGroup'

interface Props {
  visible: boolean
  recordId: string
  record?: {
    title: string
    cover_url?: string
    cover_image?: string
    industry?: string
    match_score?: number
  }
}

const props = defineProps<Props>()

const emit = defineEmits<{
  close: []
  saved: [groupId: string]
}>()

const templateGroupStore = useTemplateGroupStore()

// State
const loading = ref(false)
const saving = ref(false)
const error = ref<string | null>(null)
const extractedData = ref<any>(null)
const elementsCollapsed = ref(false)
const coverError = ref(false)

const isSaveEnabled = computed(() => {
  const hasData = extractedData.value !== null
  const hasSelectedElements = extractedData.value?.elements?.some((e: any) => e.selected)
  const notLoading = !loading.value && !saving.value
  return hasData && hasSelectedElements && notLoading
})

const showSaveHint = computed(() => {
  return extractedData.value !== null && !isSaveEnabled.value
})

const saveHintText = computed(() => {
  if (!extractedData.value) return ''
  if (!extractedData.value.elements?.some((e: any) => e.selected)) return '请至少选择一个技巧'
  return ''
})

// Watch for visible changes to extract template
watch(() => props.visible, async (newVisible) => {
  if (newVisible && props.recordId) {
    await extractTemplate()
  } else if (!newVisible) {
    resetState()
  }
})

async function extractTemplate() {
  loading.value = true
  error.value = null
  extractedData.value = null

  try {
    const result = await templateGroupStore.extractTemplateGroup(props.recordId)
    if (result) {
      // 确保 elements 数组中的每个元素都有 selected 字段
      if (result.elements && Array.isArray(result.elements)) {
        result.elements = result.elements.map((element: any) => ({
          ...element,
          selected: element.selected !== false // 默认 true
        }))
      }
      extractedData.value = result
    } else {
      error.value = '提取技巧失败，请重试'
    }
  } catch (err) {
    error.value = '提取技巧时发生错误'
    console.error('Extract template error:', err)
  } finally {
    loading.value = false
  }
}

function handleRetry() {
  extractTemplate()
}

function handleClose() {
  emit('close')
}

async function handleSave() {
  if (!isSaveEnabled.value || !extractedData.value || !props.record) return

  saving.value = true
  try {
    // 构建技巧元素列表
    const selectedElements = extractedData.value.elements.filter((e: any) => e.selected)

    // 将旧的提取格式转换为新模板组格式
    const elements = selectedElements.map((element: any) => {
      let content = ''
      const examples: string[] = []

      // 优先使用 element 自身的 content 和 examples（新格式）
      if (element.content) {
        content = element.content
      } else if (element.type === 'title' && extractedData.value.title_template) {
        content = extractedData.value.title_template
      } else if (element.type === 'structure' && extractedData.value.structure_template) {
        content = extractedData.value.structure_template
      } else if (element.type === 'tone' && extractedData.value.tone_style) {
        content = extractedData.value.tone_style
      } else if (element.type === 'cta' && extractedData.value.cta_type) {
        content = extractedData.value.cta_type
      }

      // 使用 element 自身的 examples，或从 extractedData 补充
      if (element.examples && element.examples.length > 0) {
        examples.push(...element.examples)
      } else if (element.type === 'title' && props.record?.title) {
        examples.push(props.record.title)
      }

      // 如果还是没有内容，使用 description 作为最后的 fallback
      if (!content) {
        content = element.description
      }

      return {
        type: element.type,
        name: element.name,
        description: element.description,
        content: content,
        examples: examples
      }
    })

    const result = await templateGroupStore.createGroup({
      source_record_id: props.recordId,
      source_title: props.record.title,
      source_industry: props.record.industry,
      source_cover: props.record.cover_url || props.record.cover_image,
      match_score: props.record.match_score,
      elements: elements
    })

    if (result) {
      emit('saved', result.group_id)
      emit('close')
    }
  } catch (err) {
    console.error('Save template group error:', err)
    alert('保存技巧失败，请重试')
  } finally {
    saving.value = false
  }
}

function resetState() {
  loading.value = false
  saving.value = false
  error.value = null
  extractedData.value = null
  elementsCollapsed.value = false
  coverError.value = false
}

function getElementIcon(type: string): string {
  const icons: Record<string, string> = {
    title: '📝',
    structure: '🏗️',
    tone: '💬',
    cta: '🎯'
  }
  return icons[type] || '📌'
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-content {
  background: white;
  border-radius: 16px;
  width: 100%;
  max-width: 520px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #f0f0f0;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.header-title .icon {
  font-size: 24px;
}

.header-title h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.close-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: #f5f5f5;
  border-radius: 50%;
  font-size: 24px;
  line-height: 1;
  cursor: pointer;
  color: #666;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.close-btn:hover {
  background: #e8e8e8;
  color: #333;
}

.modal-body {
  padding: 24px;
  overflow-y: auto;
  flex: 1;
}

.record-preview {
  display: flex;
  gap: 14px;
  padding: 14px;
  background: #f9f9f9;
  border-radius: 12px;
  margin-bottom: 20px;
}

.preview-cover {
  width: 60px;
  height: 80px;
  border-radius: 8px;
  overflow: hidden;
  background: #e8e8e8;
  flex-shrink: 0;
}

.preview-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.preview-info {
  display: flex;
  flex-direction: column;
  gap: 6px;
  justify-content: center;
  flex: 1;
  min-width: 0;
}

.preview-title {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #333;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.preview-industry {
  font-size: 12px;
  color: #999;
  background: white;
  padding: 4px 10px;
  border-radius: 12px;
  align-self: flex-start;
}

.loading-section {
  text-align: center;
  padding: 30px 20px;
}

.skeleton-loader {
  margin-bottom: 20px;
}

.skeleton-header {
  height: 40px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e8e8e8 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 8px;
  margin-bottom: 16px;
}

.skeleton-item {
  height: 56px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e8e8e8 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 8px;
  margin-bottom: 12px;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.loading-text {
  font-size: 14px;
  color: #666;
  margin: 0;
}

.error-section {
  text-align: center;
  padding: 30px 20px;
}

.error-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.error-text {
  font-size: 14px;
  color: #666;
  margin: 0 0 20px 0;
}

.retry-btn {
  padding: 10px 24px;
  border: 1px solid var(--primary, #ff2442);
  background: white;
  color: var(--primary, #ff2442);
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.retry-btn:hover {
  background: rgba(255, 36, 66, 0.05);
}

.extracted-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.elements-card {
  border: 1px solid #e8e8e8;
  border-radius: 12px;
  overflow: hidden;
}

.elements-card.collapsed .elements-list {
  display: none;
}

.elements-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 16px;
  background: linear-gradient(135deg, #fff5f5 0%, #fff0f0 100%);
  border-bottom: 1px solid #ffe8e8;
}

.elements-icon {
  font-size: 18px;
}

.elements-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--primary, #ff2442);
}

.elements-list {
  padding: 8px 0;
}

.element-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px 16px;
  cursor: pointer;
  transition: background 0.2s;
}

.element-item:hover {
  background: #f9f9f9;
}

.element-checkbox {
  margin-top: 4px;
  width: 18px;
  height: 18px;
  accent-color: var(--primary, #ff2442);
}

.element-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
}

.element-type {
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.element-desc {
  font-size: 13px;
  color: #666;
  line-height: 1.5;
}

.toggle-btn {
  width: 100%;
  padding: 12px 16px;
  border: none;
  background: #f9f9f9;
  color: #666;
  font-size: 13px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  transition: background 0.2s;
  border-top: 1px solid #f0f0f0;
}

.toggle-btn:hover {
  background: #f0f0f0;
}

.toggle-arrow {
  font-size: 12px;
}

.hint-section {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 12px 14px;
  background: #f0f9ff;
  border: 1px solid #bae6fd;
  border-radius: 10px;
}

.hint-icon {
  font-size: 16px;
  flex-shrink: 0;
}

.hint-text {
  font-size: 13px;
  color: #0c4a6e;
  line-height: 1.5;
}

.modal-footer {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 20px 24px;
  border-top: 1px solid #f0f0f0;
  background: #fafafa;
}

.footer-hint {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: #fff7e6;
  border: 1px solid #ffd591;
  border-radius: 8px;
}

.hint-icon {
  font-size: 14px;
}

.hint-text {
  font-size: 13px;
  color: #d46b08;
}

.footer-buttons {
  display: flex;
  gap: 12px;
}

.footer-btn {
  flex: 1;
  padding: 12px 20px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.footer-btn.secondary {
  border: 1px solid #e0e0e0;
  background: white;
  color: #333;
}

.footer-btn.secondary:hover:not(:disabled) {
  border-color: #ccc;
}

.footer-btn.primary {
  border: none;
  background: var(--primary, #ff2442);
  color: white;
}

.footer-btn.primary:hover:not(:disabled) {
  background: #e61f37;
}

.footer-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.collapse-enter-active,
.collapse-leave-active {
  transition: all 0.3s ease;
  overflow: hidden;
}

.collapse-enter-from,
.collapse-leave-to {
  max-height: 0;
  opacity: 0;
}

.collapse-enter-to,
.collapse-leave-from {
  max-height: 300px;
  opacity: 1;
}

.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.2s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}
</style>
