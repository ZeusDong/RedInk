<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="visible" class="modal-overlay" @click.self="handleClose">
        <div class="confirm-modal">
          <!-- Header -->
          <header class="modal-header">
            <h2 class="modal-title">AI 分析确认</h2>
            <button class="close-btn" @click="handleClose" title="关闭">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
              </svg>
            </button>
          </header>

          <!-- Body -->
          <div class="modal-body">
            <!-- 战略背景 -->
            <section class="form-section">
              <h3 class="section-title">【战略背景】</h3>

              <div class="form-group">
                <label class="form-label required">所属赛道</label>
                <select v-model="formData.industry" class="form-select" :class="{ error: errors.industry }">
                  <option value="">请选择</option>
                  <option value="AI工具">AI工具</option>
                  <option value="职场搞钱">职场搞钱</option>
                  <option value="情感咨询">情感咨询</option>
                  <option value="美妆护肤">美妆护肤</option>
                  <option value="服饰穿搭">服饰穿搭</option>
                  <option value="美食">美食</option>
                  <option value="旅行">旅行</option>
                  <option value="家居">家居</option>
                  <option value="健身">健身</option>
                  <option value="教育">教育</option>
                  <option value="其他">其他</option>
                </select>
                <span v-if="errors.industry" class="form-error">{{ errors.industry }}</span>
              </div>

              <div class="form-row">
                <div class="form-group">
                  <label class="form-label required">账号粉丝量</label>
                  <input
                    v-model.number="formData.follower_count"
                    type="number"
                    min="0"
                    class="form-input"
                    :class="{ error: errors.follower_count }"
                    placeholder="0"
                  />
                  <span v-if="errors.follower_count" class="form-error">{{ errors.follower_count }}</span>
                </div>

                <div class="form-group">
                  <label class="form-label">发布时间</label>
                  <input
                    v-model="formData.published_at"
                    type="date"
                    class="form-input"
                  />
                </div>
              </div>

              <div class="form-group">
                <label class="form-label required">数据表现</label>
                <div class="metrics-inputs">
                  <div class="metric-input">
                    <span class="metric-label">👍 点赞</span>
                    <input
                      v-model.number="formData.likes_count"
                      type="number"
                      min="0"
                      class="form-input"
                      :class="{ error: errors.likes_count }"
                    />
                  </div>
                  <div class="metric-input">
                    <span class="metric-label">💾 收藏</span>
                    <input
                      v-model.number="formData.saves_count"
                      type="number"
                      min="0"
                      class="form-input"
                      :class="{ error: errors.saves_count }"
                    />
                  </div>
                  <div class="metric-input">
                    <span class="metric-label">💬 评论</span>
                    <input
                      v-model.number="formData.comments_count"
                      type="number"
                      min="0"
                      class="form-input"
                      :class="{ error: errors.comments_count }"
                    />
                  </div>
                </div>
                <span v-if="errors.metrics" class="form-error">{{ errors.metrics }}</span>
              </div>
            </section>

            <!-- 内容本体 -->
            <section class="form-section">
              <h3 class="section-title">【内容本体】</h3>

              <div class="form-group">
                <label class="form-label required">标题/封面文案</label>
                <input
                  v-model="formData.title"
                  type="text"
                  class="form-input"
                  :class="{ error: errors.title }"
                  placeholder="请输入标题"
                  maxlength="100"
                />
                <span class="char-count">{{ formData.title.length }}/100</span>
                <span v-if="errors.title" class="form-error">{{ errors.title }}</span>
              </div>

              <div class="form-group">
                <label class="form-label required">正文/脚本全文</label>
                <textarea
                  v-model="formData.content"
                  class="form-textarea"
                  :class="{ error: errors.content }"
                  placeholder="请输入正文内容..."
                  rows="6"
                ></textarea>
                <span v-if="errors.content" class="form-error">{{ errors.content }}</span>
              </div>
            </section>

            <!-- 视觉与互动 -->
            <section class="form-section">
              <h3 class="section-title">【视觉与互动】</h3>

              <div class="form-group">
                <label class="form-label required">视觉描述</label>
                <div class="visual-desc-wrapper">
                  <textarea
                    v-model="formData.visual_description"
                    class="form-textarea"
                    :class="{ error: errors.visual_description }"
                    placeholder="描述图片的视觉风格、配色、构图等..."
                    rows="4"
                  ></textarea>
                  <button
                    v-if="record?.cover_image || (record?.images?.length > 0)"
                    class="ai-generate-btn"
                    @click="handleGenerateVisualDesc"
                    :disabled="generatingVisual"
                    title="AI 生成视觉描述"
                  >
                    <svg v-if="!generatingVisual" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M21 12a9 9 0 1 1-6.219-8.56"></path>
                      <path d="M9 12h6"></path>
                    </svg>
                    <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="spin">
                      <path d="M21 12a9 9 0 1 1-6.219-8.56"></path>
                    </svg>
                    {{ generatingVisual ? '生成中...' : 'AI 生成' }}
                  </button>
                </div>
                <span v-if="errors.visual_description" class="form-error">{{ errors.visual_description }}</span>
              </div>

              <div class="form-group">
                <label class="form-label">高赞评论</label>
                <div class="comments-list">
                  <div v-for="(comment, index) in formData.top_comments" :key="index" class="comment-item">
                    <textarea
                      v-model="formData.top_comments[index]"
                      class="form-textarea comment-textarea"
                      :placeholder="`评论 ${index + 1}`"
                      rows="2"
                    ></textarea>
                    <button class="remove-comment-btn" @click="removeComment(index)" title="删除">
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="18" y1="6" x2="6" y2="18"></line>
                        <line x1="6" y1="6" x2="18" y2="18"></line>
                      </svg>
                    </button>
                  </div>
                  <button class="add-comment-btn" @click="addComment">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <line x1="12" y1="5" x2="12" y2="19"></line>
                      <line x1="5" y1="12" x2="19" y2="12"></line>
                    </svg>
                    添加评论
                  </button>
                </div>
              </div>
            </section>
          </div>

          <!-- Footer -->
          <footer class="modal-footer">
            <button class="btn btn-secondary" @click="handleSaveDraft" :disabled="saving">
              {{ saving ? '保存中...' : '保存草稿' }}
            </button>
            <button class="btn btn-primary" @click="handleSubmit" :disabled="submitting">
              <svg v-if="!submitting" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 12a9 9 0 1 1-6.219-8.56"></path>
              </svg>
              <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="spin">
                <path d="M21 12a9 9 0 1 1-6.219-8.56"></path>
              </svg>
              {{ submitting ? '分析中...' : '开始 AI 分析' }}
            </button>
          </footer>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, reactive, watch, onMounted } from 'vue'
import type { ReferenceRecord } from '@/api'

interface Props {
  visible: boolean
  record: ReferenceRecord | null
}

interface Emits {
  (e: 'close'): void
  (e: 'save-draft', data: any): void
  (e: 'submit', data: any): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// 表单数据
const formData = reactive({
  record_id: '',
  industry: '',
  follower_count: 0,
  published_at: '',
  likes_count: 0,
  saves_count: 0,
  comments_count: 0,
  title: '',
  content: '',
  visual_description: '',
  top_comments: [] as string[]
})

// 验证错误
const errors = reactive<Record<string, string>>({})

// 状态
const saving = ref(false)
const submitting = ref(false)
const generatingVisual = ref(false)

// 初始化表单数据
onMounted(() => {
  loadDraftOrRecord()
})

// 监听 record 变化
watch(() => props.record, () => {
  if (props.record) {
    loadDraftOrRecord()
  }
})

// 监听 visible 变化
watch(() => props.visible, (visible) => {
  if (visible) {
    loadDraftOrRecord()
  }
})

async function loadDraftOrRecord() {
  if (!props.record) return

  // 先尝试加载草稿
  try {
    const response = await fetch(`/api/analysis/draft?record_id=${props.record.record_id}`)
    const result = await response.json()

    if (result.success && result.data) {
      // 加载草稿数据
      Object.assign(formData, {
        record_id: result.data.record_id || props.record.record_id,
        industry: result.data.industry || '',
        follower_count: result.data.follower_count || 0,
        published_at: result.data.published_at ? result.data.published_at.split('T')[0] : '',
        likes_count: result.data.likes_count || 0,
        saves_count: result.data.saves_count || 0,
        comments_count: result.data.comments_count || 0,
        title: result.data.title || '',
        content: result.data.content || '',
        visual_description: result.data.visual_description || '',
        top_comments: result.data.top_comments || []
      })
      return
    }
  } catch (e) {
    console.error('[AnalyzeConfirmModal] Failed to load draft:', e)
  }

  // 从 record 加载数据
  formData.record_id = props.record.record_id
  formData.industry = props.record.industry || ''
  formData.follower_count = props.record.blogger?.follower_count || 0
  formData.published_at = props.record.created_at ? props.record.created_at.split('T')[0] : ''
  formData.likes_count = props.record.metrics?.likes || 0
  formData.saves_count = props.record.metrics?.saves || 0
  formData.comments_count = props.record.metrics?.comments || 0
  formData.title = props.record.title || ''
  formData.content = props.record.body || ''
  formData.visual_description = ''
  formData.top_comments = []
}

function validate(): boolean {
  // 清空错误
  Object.keys(errors).forEach(key => delete errors[key])

  let isValid = true

  if (!formData.industry) {
    errors.industry = '请选择所属赛道'
    isValid = false
  }

  if (formData.follower_count < 0) {
    errors.follower_count = '粉丝量不能为负数'
    isValid = false
  }

  if (!formData.likes_count || formData.likes_count < 0) {
    errors.metrics = '请输入有效的点赞数'
    isValid = false
  }

  if (!formData.saves_count || formData.saves_count < 0) {
    errors.metrics = '请输入有效的收藏数'
    isValid = false
  }

  if (!formData.comments_count || formData.comments_count < 0) {
    errors.metrics = '请输入有效的评论数'
    isValid = false
  }

  if (!formData.title.trim()) {
    errors.title = '请输入标题'
    isValid = false
  }

  if (!formData.content.trim()) {
    errors.content = '请输入正文内容'
    isValid = false
  }

  if (!formData.visual_description.trim()) {
    errors.visual_description = '请输入视觉描述或使用 AI 生成'
    isValid = false
  }

  return isValid
}

async function handleSaveDraft() {
  if (!validate()) return

  saving.value = true
  try {
    const response = await fetch('/api/analysis/draft', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(formData)
    })
    const result = await response.json()

    if (result.success) {
      emit('save-draft', result.data)
      handleClose()
    } else {
      alert(result.error || '保存失败，请重试')
    }
  } catch (e) {
    console.error('[AnalyzeConfirmModal] Failed to save draft:', e)
    alert('保存失败，请检查网络连接')
  } finally {
    saving.value = false
  }
}

async function handleSubmit() {
  if (!validate()) return

  submitting.value = true
  try {
    const response = await fetch('/api/analysis/submit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(formData)
    })
    const result = await response.json()

    if (result.success) {
      emit('submit', result.data)
      handleClose()
    } else {
      alert(result.error || '提交失败，请重试')
    }
  } catch (e) {
    console.error('[AnalyzeConfirmModal] Failed to submit:', e)
    alert('提交失败，请检查网络连接')
  } finally {
    submitting.value = false
  }
}

async function handleGenerateVisualDesc() {
  if (!props.record) return

  generatingVisual.value = true
  try {
    // 默认选择封面图和第一张内容图
    const imageIndices = [-1]
    if (props.record.images && props.record.images.length > 0) {
      imageIndices.push(0)
    }

    const response = await fetch('/api/analysis/visual-desc', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        record_id: props.record.record_id,
        image_indices: imageIndices
      })
    })
    const result = await response.json()

    if (result.success && result.data?.description) {
      formData.visual_description = result.data.description
    } else {
      alert(result.error || 'AI 生成失败，请手动输入')
    }
  } catch (e) {
    console.error('[AnalyzeConfirmModal] Failed to generate visual description:', e)
    alert('AI 生成失败，请检查网络连接')
  } finally {
    generatingVisual.value = false
  }
}

function addComment() {
  formData.top_comments.push('')
}

function removeComment(index: number) {
  formData.top_comments.splice(index, 1)
}

function handleClose() {
  // 检查是否有未保存的更改
  const hasChanges = formData.visual_description || formData.top_comments.some(c => c.trim())
  if (hasChanges && !confirm('确定要关闭吗？未保存的内容将会丢失。')) {
    return
  }
  emit('close')
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.confirm-modal {
  background: white;
  border-radius: 16px;
  width: 100%;
  max-width: 600px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
}

/* 模态框动画 */
.modal-enter-active,
.modal-leave-active {
  transition: all 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .confirm-modal,
.modal-leave-to .confirm-modal {
  transform: scale(0.9) translateY(-20px);
}

/* Header */
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e8e6e3;
}

.modal-title {
  font-size: 18px;
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

/* Body */
.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.form-section {
  margin-bottom: 24px;
}

.form-section:last-child {
  margin-bottom: 0;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0 0 16px 0;
  padding-bottom: 8px;
  border-bottom: 2px solid #ff2442;
  display: inline-block;
}

.form-group {
  margin-bottom: 16px;
  position: relative;
}

.form-row {
  display: flex;
  gap: 16px;
}

.form-row .form-group {
  flex: 1;
}

.form-label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: #333;
  margin-bottom: 6px;
}

.form-label.required::after {
  content: ' *';
  color: #ff2442;
}

.form-input,
.form-select,
.form-textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  color: #333;
  transition: all 0.2s;
  font-family: inherit;
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
  outline: none;
  border-color: #ff2442;
  box-shadow: 0 0 0 3px rgba(255, 36, 66, 0.1);
}

.form-input.error,
.form-select.error,
.form-textarea.error {
  border-color: #ff2442;
}

.form-error {
  display: block;
  font-size: 12px;
  color: #ff2442;
  margin-top: 4px;
}

.char-count {
  position: absolute;
  right: 12px;
  bottom: -20px;
  font-size: 11px;
  color: #999;
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
}

/* Metrics Inputs */
.metrics-inputs {
  display: flex;
  gap: 12px;
}

.metric-input {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
  background: #f8f7f5;
  padding: 8px 12px;
  border-radius: 8px;
  border: 1px solid #e8e6e3;
}

.metric-label {
  font-size: 12px;
  color: #666;
  white-space: nowrap;
}

.metric-input .form-input {
  flex: 1;
  min-width: 60px;
  border: none;
  background: transparent;
  padding: 4px 8px;
  font-size: 14px;
}

/* Visual Description */
.visual-desc-wrapper {
  position: relative;
}

.ai-generate-btn {
  position: absolute;
  right: 8px;
  bottom: 8px;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  background: #ff2442;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.ai-generate-btn:hover:not(:disabled) {
  background: #e61e3a;
}

.ai-generate-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.ai-generate-btn svg.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Comments */
.comments-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.comment-item {
  display: flex;
  gap: 8px;
  align-items: flex-start;
}

.comment-textarea {
  flex: 1;
  min-height: 60px;
  font-size: 13px;
}

.remove-comment-btn {
  width: 28px;
  height: 28px;
  border: none;
  background: #f8f7f5;
  color: #999;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  flex-shrink: 0;
}

.remove-comment-btn:hover {
  background: #ffeee8;
  color: #ff2442;
}

.add-comment-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border: 1px dashed #ddd;
  background: transparent;
  color: #666;
  border-radius: 8px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
  width: 100%;
  justify-content: center;
}

.add-comment-btn:hover {
  border-color: #ff2442;
  color: #ff2442;
  background: #ffeee8;
}

/* Footer */
.modal-footer {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  padding: 16px 24px;
  border-top: 1px solid #e8e6e3;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border-radius: 8px;
  border: none;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.btn-secondary {
  background: #f8f7f5;
  color: #333;
}

.btn-secondary:hover:not(:disabled) {
  background: #e8e6e3;
}

.btn-primary {
  background: #ff2442;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #e61e3a;
}

.btn-primary svg.spin {
  animation: spin 1s linear infinite;
}
</style>
