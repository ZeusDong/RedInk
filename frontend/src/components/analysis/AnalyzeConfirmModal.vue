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

              <!-- 图片选择区域 -->
              <div v-if="hasImages" class="image-selection-area">
                <!-- 封面图 -->
                <div class="image-group cover-group">
                  <label class="group-label">【封面图】</label>
                  <div class="image-checkbox" :class="{ checked: coverSelected, error: coverLoadError }">
                    <!-- Badge for cover image (index -1) -->
                    <span
                      v-if="getBadgeState(-1) !== 'none'"
                      class="image-badge"
                      :class="getBadgeState(-1)"
                      :title="getBadgeTitle(getBadgeState(-1))"
                    >
                      {{ getBadgeIcon(getBadgeState(-1)) }}
                    </span>

                    <input type="checkbox" v-model="coverSelected" />
                    <img
                      v-if="record?.cover_image"
                      :src="record.cover_image"
                      @error="handleCoverError"
                      alt="封面图"
                    />
                    <div v-else class="image-placeholder">
                      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                        <circle cx="8.5" cy="8.5" r="1.5"></circle>
                        <polyline points="21 15 16 10 5 21"></polyline>
                      </svg>
                    </div>
                    <span v-if="coverLoadError" class="load-error-icon" title="图片加载失败">⚠️</span>
                  </div>
                </div>

                <!-- 内容图 -->
                <div v-if="record?.images?.length" class="image-group content-group">
                  <label class="group-label">【内容图】({{ record.images.length }}张)</label>
                  <div class="content-images-grid">
                    <div
                      v-for="(img, idx) in record.images"
                      :key="idx"
                      class="image-checkbox"
                      :class="{ checked: isContentImageSelected(idx), error: contentLoadErrors.has(idx) }"
                    >
                      <!-- Badge for content image -->
                      <span
                        v-if="getBadgeState(idx) !== 'none'"
                        class="image-badge"
                        :class="getBadgeState(idx)"
                        :title="getBadgeTitle(getBadgeState(idx))"
                      >
                        {{ getBadgeIcon(getBadgeState(idx)) }}
                      </span>
                      <input
                        type="checkbox"
                        :checked="isContentImageSelected(idx)"
                        @change="toggleContentImage(idx)"
                      />
                      <img
                        v-if="!contentLoadErrors.has(idx)"
                        :src="img"
                        @error="() => handleContentError(idx)"
                        :alt="`内容图${idx + 1}`"
                      />
                      <div v-else class="image-error-placeholder" :title="img">
                        <span class="error-text">加载失败</span>
                      </div>
                      <span class="image-label">图{{ idx + 1 }}</span>
                      <span v-if="contentLoadErrors.has(idx)" class="load-error-icon" title="图片加载失败">⚠️</span>
                    </div>
                  </div>
                  <div class="quick-actions">
                    <button type="button" @click="selectAllContent">全选</button>
                    <button type="button" @click="clearAllContent">清空选择</button>
                  </div>
                </div>
              </div>

              <!-- 无图片提示 -->
              <div v-else class="no-images-message">
                <p>⚠️ 暂无可用图片</p>
                <p>该笔记没有封面图或内容图，请手动输入视觉描述</p>
              </div>

              <!-- 操作栏 -->
              <div v-if="hasImages" class="visual-action-bar">
                <div class="action-left">
                  <span class="selection-count">已选择 {{ selectedCount }} 张图片</span>
                  <!-- 追加/覆盖模式切换 -->
                  <div class="mode-toggle" v-if="formData.visual_description">
                    <button
                      type="button"
                      class="mode-btn"
                      :class="{ active: visualDescMode === 'append' }"
                      @click="visualDescMode = 'append'"
                      title="新生成的描述将追加到现有描述后面"
                    >
                      追加
                    </button>
                    <button
                      type="button"
                      class="mode-btn"
                      :class="{ active: visualDescMode === 'replace' }"
                      @click="visualDescMode = 'replace'"
                      title="新生成的描述将替换现有描述"
                    >
                      覆盖
                    </button>
                  </div>
                </div>
                <button
                  type="button"
                  class="btn-generate"
                  @click="handleGenerateVisualDesc"
                  :disabled="selectedCount === 0 || generatingVisual"
                >
                  <svg v-if="!generatingVisual" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 12a9 9 0 1 1-6.219-8.56"></path>
                  </svg>
                  <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="spin">
                    <path d="M21 12a9 9 0 1 1-6.219-8.56"></path>
                  </svg>
                  {{ generatingVisual ? '生成中...' : '生成视觉描述' }}
                </button>
              </div>

              <!-- 视觉描述 -->
              <div class="form-group">
                <label class="form-label required">视觉描述</label>
                <textarea
                  v-model="formData.visual_description"
                  class="form-textarea"
                  :class="{ error: errors.visual_description }"
                  :placeholder="hasImages ? '请先选择图片，然后点击「生成视觉描述」' : '描述图片的视觉风格、配色、构图等...'"
                  :readonly="generatingVisual"
                  rows="4"
                ></textarea>
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
import { ref, reactive, watch, onMounted, computed } from 'vue'
import type { ReferenceRecord } from '@/api'
import { useImageDescriptionBadge } from '@/composables/useImageDescriptionBadge'
import type { ImageDescription } from '@/types/analysis'

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

// 视觉描述生成模式：'append'（追加）或 'replace'（覆盖）
const visualDescMode = ref<'append' | 'replace'>('append')

// ========== 新增：图片选择状态 ==========

// 选中的图片索引（-1=封面，0+=内容图）
const selectedImageIndices = ref<number[]>([-1])  // 默认选中封面

// 图片加载错误状态
const coverLoadError = ref(false)
const contentLoadErrors = ref<Set<number>>(new Set())

// 本地图片检查状态
const hasCheckedLocal = ref(false)

// ========== 新增：图片描述元数据 ==========

// Image description metadata per image index
const imageDescriptions = ref<Record<number, ImageDescription>>({})

// Use the badge composable
const {
  getBadgeState,
  getBadgeIcon,
  getBadgeTitle
} = useImageDescriptionBadge({
  imageDescriptions,
  visualDescription: formData.visual_description  // Pass string directly, composable will wrap in ref
})

// ========== 新增：计算属性 ==========

// 是否有可用图片
const hasImages = computed(() => {
  return !!(props.record?.cover_image || (props.record?.images && props.record.images.length > 0))
})

// 已选中图片数量
const selectedCount = computed(() => {
  return selectedImageIndices.value.length
})

// 封面图是否选中（双向绑定computed）
const coverSelected = computed({
  get: () => selectedImageIndices.value.includes(-1),
  set: (val: boolean) => {
    if (val && !selectedImageIndices.value.includes(-1)) {
      selectedImageIndices.value.push(-1)
    } else if (!val) {
      selectedImageIndices.value = selectedImageIndices.value.filter(i => i !== -1)
    }
  }
})

// 初始化表单数据
onMounted(() => {
  checkLocalImages()
  loadDraftOrRecord()
})

// 监听 record 变化
watch(() => props.record, (newRecord) => {
  if (newRecord) {
    // Debug: 打印图片信息
    console.log('[AnalyzeConfirmModal] Record changed, images count:', newRecord.images?.length || 0)
    console.log('[AnalyzeConfirmModal] Image URLs:', newRecord.images)
    console.log('[AnalyzeConfirmModal] Cover image:', newRecord.cover_image)
    // 重置本地检查状态并检查本地图片
    hasCheckedLocal.value = false
    checkLocalImages()
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

      // Load image descriptions from draft
      if (result.data.image_descriptions) {
        imageDescriptions.value = result.data.image_descriptions
      } else {
        imageDescriptions.value = {}
      }

      return
    }
  } catch (e) {
    console.error('[AnalyzeConfirmModal] Failed to load draft:', e)
  }

  // 从 record 加载数据
  formData.record_id = props.record.record_id
  // Clear image descriptions when loading from record (not draft)
  imageDescriptions.value = {}
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
    // Add image description metadata to draft data
    const draftData = {
      ...formData,
      // Add image description metadata
      image_descriptions: imageDescriptions.value,
      generated_image_indices: Object.keys(imageDescriptions.value).map(Number)
    }

    const response = await fetch('/api/analysis/draft', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(draftData)
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

  // 验证：至少选择一张图片
  if (selectedCount.value === 0) {
    alert('请先选择至少一张图片')
    return
  }

  // 覆盖模式下，如果已有描述需要确认
  if (visualDescMode.value === 'replace' && formData.visual_description) {
    if (!confirm('确定要覆盖现有的视觉描述吗？')) {
      return
    }
  }

  generatingVisual.value = true
  try {
    const response = await fetch('/api/analysis/visual-desc', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        record_id: props.record.record_id,
        image_indices: selectedImageIndices.value
      })
    })
    const result = await response.json()

    if (result.success && result.data?.description) {
      const newDescription = result.data.description

      // Mark images as generated - assign unique ID to each image
      const indicesToUpdate: number[] = []
      if (selectedImageIndices.value.includes(-1)) {
        indicesToUpdate.push(-1) // Cover image index
      }
      selectedImageIndices.value.forEach(idx => {
        if (idx >= 0) {  // Only content images (0+)
          indicesToUpdate.push(idx)
        }
      })

      // Save description with unique ID for EACH image
      indicesToUpdate.forEach(idx => {
        // Generate unique ID per image: timestamp-random-index
        const uniqueDescId = `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}-${idx}`

        imageDescriptions.value[idx] = {
          id: uniqueDescId,
          content: newDescription
        }
      })

      // Add to form with ID markers (one for each image)
      const markedDescriptions = indicesToUpdate.map(idx => {
        const desc = imageDescriptions.value[idx]
        return `<!-- DESC-${desc.id} -->\n${newDescription}`
      }).join('\n\n---\n\n')

      // 根据模式决定是追加还是覆盖
      if (visualDescMode.value === 'append' && formData.visual_description) {
        // 追加模式：在现有描述后添加新描述，用分隔符隔开
        formData.visual_description = formData.visual_description + '\n\n---\n\n' + markedDescriptions
      } else {
        // 覆盖模式或首次生成
        formData.visual_description = markedDescriptions
      }
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

// ========== 新增：图片描述清除方法 ==========

/**
 * Clear all image description metadata (e.g., when user clears form)
 */
function clearImageDescriptions() {
  imageDescriptions.value = {}
}

/**
 * Clear description for specific image index
 */
function clearImageDescription(idx: number) {
  delete imageDescriptions.value[idx]
}

function handleClose() {
  // 检查是否有未保存的更改
  const hasChanges = formData.visual_description || formData.top_comments.some(c => c.trim())
  if (hasChanges && !confirm('确定要关闭吗？未保存的内容将会丢失。')) {
    return
  }
  emit('close')
}

// ========== 新增：图片选择方法 ==========

/**
 * 检查内容图是否被选中
 */
function isContentImageSelected(idx: number): boolean {
  return selectedImageIndices.value.includes(idx)
}

/**
 * 切换内容图选中状态
 */
function toggleContentImage(idx: number): void {
  const index = selectedImageIndices.value.indexOf(idx)
  if (index > -1) {
    selectedImageIndices.value.splice(index, 1)
  } else {
    selectedImageIndices.value.push(idx)
  }
}

/**
 * 全选内容图
 */
function selectAllContent(): void {
  if (!props.record?.images) return
  props.record.images.forEach((_, idx) => {
    if (!selectedImageIndices.value.includes(idx)) {
      selectedImageIndices.value.push(idx)
    }
  })
}

/**
 * 清空内容图选择
 */
function clearAllContent(): void {
  selectedImageIndices.value = selectedImageIndices.value.filter(i => i === -1)
}

/**
 * 处理封面图加载失败
 */
function handleCoverError(): void {
  console.warn('[AnalyzeConfirmModal] Cover image failed to load:', props.record?.cover_image)
  coverLoadError.value = true
}

/**
 * 处理内容图加载失败
 */
function handleContentError(idx: number): void {
  const imgUrl = props.record?.images?.[idx]
  console.warn(`[AnalyzeConfirmModal] Content image ${idx} failed to load:`, imgUrl)
  contentLoadErrors.value.add(idx)
}

/**
 * 检查本地是否有图片
 */
async function checkLocalImages() {
  if (!props.record) return

  try {
    const { checkReferenceImages } = await import('@/api')
    const result = await checkReferenceImages(props.record.record_id)

    // 先清空数据中的图片链接（可能是过期的飞书图片）
    if (props.record) {
      props.record.images = []
    }

    // 只使用本地存在的图片
    if (result.exists && result.images.length > 0) {
      if (props.record) {
        props.record.images = result.images
      }
    }

    hasCheckedLocal.value = true
    console.log('[AnalyzeConfirmModal] Local images check result:', result)
  } catch (e) {
    console.error('[AnalyzeConfirmModal] Failed to check local images:', e)
    hasCheckedLocal.value = true
  }
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

/* ========== 图片选择区域 ========== */
.image-selection-area {
  margin-bottom: 16px;
}

.image-group {
  margin-bottom: 16px;
}

.group-label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: #333;
  margin-bottom: 8px;
}

/* 图片复选框 */
.image-checkbox {
  position: relative;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  border: 2px solid #ddd;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  background: white;
}

.image-checkbox.checked {
  border-color: #ff2442;
  background: #ffeee8;
}

.image-checkbox:hover {
  transform: scale(1.05);
}

.image-checkbox input[type="checkbox"] {
  position: absolute;
  top: 4px;
  left: 4px;
  width: 16px;
  height: 16px;
  cursor: pointer;
  z-index: 1;
}

.image-checkbox img {
  display: block;
  object-fit: cover;
  border-radius: 4px;
}

/* 封面图尺寸 */
.cover-group .image-checkbox {
  display: inline-flex;
}

.cover-group .image-checkbox img {
  width: 80px;
  height: 80px;
}

/* 内容图网格 */
.content-images-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
  margin-bottom: 8px;
}

.content-images-grid .image-checkbox {
  display: flex;
  flex-direction: column;
  padding: 6px;
}

.content-images-grid .image-checkbox img {
  width: 60px;
  height: 60px;
}

.image-label {
  font-size: 11px;
  color: #666;
  text-align: center;
  margin-top: 2px;
}

.load-error-icon {
  position: absolute;
  top: 2px;
  right: 2px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 50%;
  width: 18px;
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
}

.image-checkbox.error {
  opacity: 0.7;
}

.image-placeholder {
  width: 80px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f0f0f0;
  border-radius: 4px;
  color: #999;
}

.image-error-placeholder {
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fff0f0;
  border-radius: 4px;
  color: #ff2442;
}

.image-error-placeholder .error-text {
  font-size: 10px;
  text-align: center;
  padding: 4px;
}

/* 快捷操作 */
.quick-actions {
  display: flex;
  gap: 8px;
}

.quick-actions button {
  padding: 4px 12px;
  font-size: 12px;
  border: 1px dashed #ddd;
  background: transparent;
  color: #666;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.quick-actions button:hover {
  border-color: #ff2442;
  color: #ff2442;
}

/* 操作栏 */
.visual-action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: #f8f7f5;
  border-radius: 8px;
  margin-bottom: 16px;
  gap: 12px;
}

.action-left {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.selection-count {
  font-size: 13px;
  color: #666;
  white-space: nowrap;
}

/* 模式切换按钮 */
.mode-toggle {
  display: inline-flex;
  background: #e8e6e3;
  border-radius: 6px;
  padding: 2px;
  gap: 2px;
}

.mode-btn {
  padding: 4px 12px;
  font-size: 12px;
  border: none;
  background: transparent;
  color: #666;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
  font-weight: 500;
}

.mode-btn:hover {
  color: #333;
}

.mode-btn.active {
  background: white;
  color: #ff2442;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.btn-generate {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: #ff2442;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-generate:hover:not(:disabled) {
  background: #e61e3a;
}

.btn-generate:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-generate svg.spin {
  animation: spin 1s linear infinite;
}

/* 无图片提示 */
.no-images-message {
  padding: 16px;
  background: #fff8f0;
  border: 1px solid #ffcc00;
  border-radius: 8px;
  margin-bottom: 16px;
  text-align: center;
}

.no-images-message p {
  margin: 4px 0;
  font-size: 13px;
  color: #666;
}

/* 响应式：移动端调整为2列 */
@media (max-width: 480px) {
  .content-images-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

/* ========== Image Badge Styles ========== */
.image-badge {
  position: absolute;
  top: -6px;
  right: -6px;
  width: 20px;
  height: 20px;
  border: 2px solid white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: white;
  z-index: 2;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.image-badge.generated {
  background: #52c41a;
}

.image-badge.missing {
  background: #faad14;
}
</style>
