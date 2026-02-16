<template>
  <Teleport to="body">
    <Transition name="modal-fade">
      <div v-if="visible" class="modal-overlay" @click.self="handleClose">
        <div class="modal-content">
          <!-- Header -->
          <div class="modal-header">
            <div class="header-title">
              <span class="icon">📋</span>
              <h3>保存为模板</h3>
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
              <p class="loading-text">AI 正在分析笔记并提取模板元素...</p>
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
                  <span class="elements-title">AI 已提取以下元素</span>
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

              <!-- Template Form -->
              <div class="form-section">
                <div class="form-group">
                  <label for="templateName">模板名称</label>
                  <input
                    id="templateName"
                    v-model="formData.name"
                    type="text"
                    class="form-input"
                    placeholder="请输入模板名称"
                  />
                </div>

                <div class="form-group">
                  <label for="templateIndustry">适用行业</label>
                  <select
                    id="templateIndustry"
                    v-model="formData.industry"
                    class="form-select"
                  >
                    <option value="">请选择行业</option>
                    <option v-for="ind in industries" :key="ind" :value="ind">
                      {{ ind }}
                    </option>
                  </select>
                </div>

                <div class="form-group">
                  <label for="templateDesc">备注（可选）</label>
                  <textarea
                    id="templateDesc"
                    v-model="formData.description"
                    class="form-textarea"
                    placeholder="添加一些备注说明..."
                    rows="2"
                  ></textarea>
                </div>

                <!-- Advanced Options -->
                <div class="advanced-section">
                  <button
                    @click="advancedCollapsed = !advancedCollapsed"
                    class="advanced-toggle"
                    type="button"
                  >
                    <span class="advanced-icon">🛠️</span>
                    <span>高级选项</span>
                    <span class="advanced-arrow">{{ advancedCollapsed ? '▼' : '▲' }}</span>
                  </button>

                  <Transition name="collapse">
                    <div v-show="!advancedCollapsed" class="advanced-options">
                      <label class="advanced-option">
                        <input type="checkbox" v-model="advancedOptions.saveTitle" />
                        <span>保存标题模板</span>
                      </label>
                      <label class="advanced-option">
                        <input type="checkbox" v-model="advancedOptions.saveStructure" />
                        <span>保存结构框架</span>
                      </label>
                      <label class="advanced-option">
                        <input type="checkbox" v-model="advancedOptions.saveTone" />
                        <span>保存语言风格</span>
                      </label>
                      <label class="advanced-option">
                        <input type="checkbox" v-model="advancedOptions.saveCta" />
                        <span>保存互动设计</span>
                      </label>
                    </div>
                  </Transition>
                </div>
              </div>
            </div>
          </div>

          <!-- Footer -->
          <div class="modal-footer">
            <button @click="handleClose" class="footer-btn secondary" :disabled="saving">
              取消
            </button>
            <button
              @click="handleSave"
              class="footer-btn primary"
              :disabled="!canSave || saving"
            >
              {{ saving ? '保存中...' : '保存模板' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useTemplateStore } from '@/stores/template'
import type { ExtractedTemplate, ExtractedTemplateElement } from '@/types/template'

interface Props {
  visible: boolean
  recordId: string
  record?: {
    title: string
    cover_url?: string
    cover_image?: string
    industry?: string
  }
}

const props = defineProps<Props>()

const emit = defineEmits<{
  close: []
  saved: [templateId: string]
}>()

const templateStore = useTemplateStore()

// State
const loading = ref(false)
const saving = ref(false)
const error = ref<string | null>(null)
const extractedData = ref<ExtractedTemplate | null>(null)
const elementsCollapsed = ref(false)
const advancedCollapsed = ref(true)
const coverError = ref(false)

// Form data
const formData = ref({
  name: '',
  industry: '',
  description: ''
})

const advancedOptions = ref({
  saveTitle: true,
  saveStructure: true,
  saveTone: true,
  saveCta: true
})

// Industries (could be fetched from API)
const industries = ref([
  '美妆护肤',
  '服饰穿搭',
  '美食探店',
  '旅行攻略',
  '家居生活',
  '健身瑜伽',
  '职场经验',
  '情感心理',
  '教育学习',
  '科技数码',
  '其他'
])

const canSave = computed(() => {
  return (
    !loading &&
    !saving &&
    extractedData.value !== null &&
    formData.value.name.trim().length > 0 &&
    formData.value.industry.length > 0
  )
})

// Watch for visible changes to extract template
watch(() => props.visible, async (newVisible) => {
  if (newVisible && props.recordId) {
    await extractTemplate()
  } else if (!newVisible) {
    resetState()
  }
})

// Watch for record to set default industry
watch(() => props.record, (record) => {
  if (record?.industry && !formData.value.industry) {
    formData.value.industry = record.industry
  }
}, { immediate: true })

async function extractTemplate() {
  loading.value = true
  error.value = null
  extractedData.value = null

  try {
    const result = await templateStore.extractTemplate(props.recordId)
    if (result) {
      extractedData.value = result
      formData.value.name = result.suggested_name || ''
    } else {
      error.value = '提取模板失败，请重试'
    }
  } catch (err) {
    error.value = '提取模板时发生错误'
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
  if (!canSave.value || !extractedData.value) return

  saving.value = true
  try {
    // Get selected elements
    const selectedElements = extractedData.value.elements.filter(e => e.selected)

    // Build extracted elements based on advanced options and selections
    const extractedElements: any = {}
    if (advancedOptions.value.saveTitle && extractedData.value.title_template) {
      extractedElements.title_template = extractedData.value.title_template
    }
    if (advancedOptions.value.saveStructure && extractedData.value.structure_template) {
      extractedElements.structure_template = extractedData.value.structure_template
    }
    if (advancedOptions.value.saveTone && extractedData.value.tone_style) {
      extractedElements.tone_style = extractedData.value.tone_style
    }
    if (advancedOptions.value.saveCta && extractedData.value.cta_type) {
      extractedElements.cta_type = extractedData.value.cta_type
    }

    const template = await templateStore.createTemplate({
      name: formData.value.name,
      industry: formData.value.industry,
      type: 'composite',
      description: formData.value.description || undefined,
      source_record_id: props.recordId,
      extracted_elements: Object.keys(extractedElements).length > 0 ? extractedElements : undefined,
      pattern: formData.value.name,
      variables: [],
      source_records: [props.recordId]
    })

    if (template) {
      emit('saved', template.id)
      emit('close')
    }
  } catch (err) {
    console.error('Save template error:', err)
    alert('保存模板失败，请重试')
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
  advancedCollapsed.value = true
  coverError.value = false
  formData.value = {
    name: '',
    industry: props.record?.industry || '',
    description: ''
  }
  advancedOptions.value = {
    saveTitle: true,
    saveStructure: true,
    saveTone: true,
    saveCta: true
  }
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
  gap: 20px;
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

.form-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.form-input,
.form-select,
.form-textarea {
  padding: 12px 14px;
  border: 1px solid #e0e0e0;
  border-radius: 10px;
  font-size: 14px;
  transition: border-color 0.2s;
  font-family: inherit;
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
  outline: none;
  border-color: var(--primary, #ff2442);
}

.form-textarea {
  resize: vertical;
}

.advanced-section {
  border: 1px solid #e8e8e8;
  border-radius: 12px;
  overflow: hidden;
}

.advanced-toggle {
  width: 100%;
  padding: 14px 16px;
  border: none;
  background: white;
  color: #333;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: background 0.2s;
}

.advanced-toggle:hover {
  background: #f9f9f9;
}

.advanced-icon {
  font-size: 18px;
}

.advanced-arrow {
  margin-left: auto;
  font-size: 12px;
  color: #999;
}

.advanced-options {
  padding: 12px 16px;
  background: #f9f9f9;
  border-top: 1px solid #f0f0f0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.advanced-option {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  font-size: 14px;
  color: #333;
}

.advanced-option input {
  width: 18px;
  height: 18px;
  accent-color: var(--primary, #ff2442);
}

.modal-footer {
  display: flex;
  gap: 12px;
  padding: 20px 24px;
  border-top: 1px solid #f0f0f0;
  background: #fafafa;
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
