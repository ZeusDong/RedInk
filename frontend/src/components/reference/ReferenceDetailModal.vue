<template>
  <!-- 对标文案详情弹窗 -->
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="visible" class="modal-overlay" @click="$emit('close')">
        <div class="modal-container" @click.stop>
          <!-- 关闭按钮 -->
          <button class="modal-close" @click="$emit('close')">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>

          <!-- 内容区域 -->
          <div class="modal-content" v-if="record">
            <!-- 封面图 -->
            <div class="detail-cover" v-if="record.cover_image || record.images.length">
              <img
                v-if="record.cover_image"
                :src="record.cover_image"
                alt="cover"
                class="cover-image"
              />
              <div v-else class="cover-gallery">
                <img
                  v-for="(image, index) in record.images.slice(0, 3)"
                  :key="index"
                  :src="image"
                  alt="image"
                  class="gallery-image"
                />
              </div>
            </div>

            <!-- 标题和链接 -->
            <div class="detail-header">
              <h2 class="detail-title">{{ record.title || '无标题' }}</h2>
              <a
                v-if="record.note_link"
                :href="record.note_link"
                target="_blank"
                rel="noopener noreferrer"
                class="detail-link"
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
                  <polyline points="15 3 21 3 21 9"></polyline>
                  <line x1="10" y1="14" x2="21" y2="3"></line>
                </svg>
                打开原文
              </a>
            </div>

            <!-- 正文内容 -->
            <div class="detail-body" v-if="record.body">
              <div class="body-text">{{ record.body }}</div>
            </div>

            <!-- 博主信息 -->
            <div class="detail-blogger" v-if="record.blogger.nickname">
              <img
                v-if="record.blogger.avatar"
                :src="record.blogger.avatar"
                alt="avatar"
                class="blogger-avatar"
              />
              <div v-else class="blogger-avatar-placeholder">
                {{ record.blogger.nickname.charAt(0) }}
              </div>
              <div class="blogger-info">
                <div class="blogger-name">{{ record.blogger.nickname }}</div>
                <div class="blogger-meta" v-if="record.blogger.follower_count">
                  {{ formatFollowerCount(record.blogger.follower_count) }} 粉丝
                </div>
              </div>
              <a
                v-if="record.blogger.homepage"
                :href="record.blogger.homepage"
                target="_blank"
                rel="noopener noreferrer"
                class="blogger-link"
              >
                访问主页
              </a>
            </div>

            <!-- 互动数据 -->
            <div class="detail-metrics">
              <div class="metric-item">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
                </svg>
                <span>{{ formatMetric(record.metrics.likes) }}</span>
                <span class="metric-label">点赞</span>
              </div>
              <div class="metric-item">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path>
                </svg>
                <span>{{ formatMetric(record.metrics.saves) }}</span>
                <span class="metric-label">收藏</span>
              </div>
              <div class="metric-item">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                </svg>
                <span>{{ formatMetric(record.metrics.comments) }}</span>
                <span class="metric-label">评论</span>
              </div>
              <div class="metric-item" v-if="record.metrics.total_engagement">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
                </svg>
                <span>{{ formatMetric(record.metrics.total_engagement) }}</span>
                <span class="metric-label">总互动</span>
              </div>
            </div>

            <!-- 标签 -->
            <div class="detail-tags" v-if="record.tags.length">
              <span class="tag" v-for="tag in record.tags" :key="tag">
                {{ tag }}
              </span>
            </div>

            <!-- 分类信息 -->
            <div class="detail-meta">
              <span v-if="record.keyword" class="meta-item">
                <span class="meta-label">关键词:</span>
                {{ record.keyword }}
              </span>
              <span v-if="record.industry" class="meta-item">
                <span class="meta-label">行业:</span>
                {{ record.industry }}
              </span>
              <span v-if="record.note_type" class="meta-item">
                <span class="meta-label">类型:</span>
                {{ record.note_type }}
              </span>
              <span v-if="record.created_at" class="meta-item">
                <span class="meta-label">发布时间:</span>
                {{ formatDate(record.created_at) }}
              </span>
            </div>

            <!-- 所有图片 -->
            <div class="detail-images">
              <!-- 有图片时 -->
              <template v-if="displayImages.length > 0">
                <h3 class="images-title">笔记图片 ({{ displayImages.length }})</h3>
                <div class="images-grid">
                  <img
                    v-for="(image, index) in displayImages"
                    :key="index"
                    :src="image"
                    alt="image"
                    class="images-item"
                    @click="previewImage(image)"
                  />
                </div>
              </template>

              <!-- 无图片时 -->
              <template v-else-if="showEmptyState">
                <div class="images-empty-state">
                  <div class="empty-icon">📷</div>
                  <h3>图片未添加</h3>

                  <!-- 有图片URL时显示下载按钮 -->
                  <template v-if="record.images && record.images.length > 0">
                    <p class="empty-text">数据中包含图片链接，可尝试自动下载</p>
                    <div class="action-buttons">
                      <button
                        class="action-btn primary"
                        :disabled="isFetching"
                        @click="fetchImages"
                      >
                        {{ isFetching ? '⏳ 下载中...' : '🔥 下载图片' }}
                      </button>
                    </div>
                  </template>

                  <!-- 无图片URL时显示手动放置说明 -->
                  <template v-else>
                    <p class="empty-text">请手动将图片放置到以下目录：</p>
                    <div class="path-box">
                      <code>{{ manualImagePath }}</code>
                    </div>
                    <p class="empty-hint">图片命名：0.jpg, 1.jpg, 2.jpg, ...</p>

                    <div class="action-buttons">
                      <a
                        v-if="record.note_link"
                        :href="record.note_link"
                        target="_blank"
                        rel="noopener"
                        class="action-btn"
                      >
                        🔗 打开原文获取图片
                      </a>
                    </div>
                  </template>

                  <!-- 状态消息 -->
                  <div v-if="fetchMessage" class="fetch-message" :class="fetchMessage.type">
                    {{ fetchMessage.text }}
                  </div>
                </div>
              </template>

              <!-- 检查中 -->
              <template v-else>
                <div class="images-loading">
                  <span>⏳ 检查中...</span>
                </div>
              </template>
            </div>
          </div>

          <!-- 加载状态 -->
          <div class="modal-loading" v-else>
            <div class="loading-spinner"></div>
            <p>加载中...</p>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>

  <!-- 图片预览 -->
  <Transition name="modal">
    <div v-if="previewImageSrc" class="preview-overlay" @click="previewImageSrc = null">
      <img :src="previewImageSrc" alt="preview" class="preview-image" @click.stop />
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { ReferenceRecord } from '@/api'

/**
 * 对标文案详情弹窗组件
 *
 * 展示对标文案的完整信息，包括封面、标题、正文、博主、互动数据、标签等
 */

// 定义 Props
const props = defineProps<{
  visible: boolean
  record: ReferenceRecord | null
}>()

// 定义 Emits
defineEmits<{
  (e: 'close'): void
}>()

// 图片预览
const previewImageSrc = ref<string | null>(null)

// 图片获取状态
const isFetching = ref(false)
const fetchMessage = ref<{type: 'success' | 'error' | 'info', text: string} | null>(null)
const hasCheckedLocal = ref(false)

// 计算属性：显示的图片列表
const displayImages = computed(() => {
  return props.record?.images || []
})

// 判断是否显示空状态
const showEmptyState = computed(() => {
  return displayImages.value.length === 0 && hasCheckedLocal.value
})

// 获取手动放置图片的目录路径
const manualImagePath = computed(() => {
  if (!props.record) return ''
  const recordId = props.record.record_id
  return `backend/static/reference_images/${recordId}/`
})

function previewImage(src: string) {
  previewImageSrc.value = src
}

function formatFollowerCount(count: number): string {
  if (count >= 10000) {
    return (count / 10000).toFixed(1) + 'w'
  }
  return count.toString()
}

function formatMetric(count: number): string {
  if (count >= 10000) {
    return (count / 10000).toFixed(1) + 'w'
  }
  if (count >= 1000) {
    return (count / 1000).toFixed(1) + 'k'
  }
  return count.toString()
}

function formatDate(dateStr: string): string {
  const date = new Date(dateStr)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}

// 检查本地是否有图片
async function checkLocalImages() {
  if (!props.record) return

  try {
    const { checkReferenceImages } = await import('@/api')
    const result = await checkReferenceImages(props.record.record_id)

    if (result.exists && result.images.length > 0) {
      if (props.record) {
        props.record.images = result.images
      }
    }

    hasCheckedLocal.value = true
  } catch (e) {
    hasCheckedLocal.value = true
  }
}

// 从现有URL下载图片
async function fetchImages() {
  if (!props.record) return

  isFetching.value = true
  fetchMessage.value = { type: 'info', text: '正在下载图片...' }

  try {
    const { fetchReferenceImages } = await import('@/api')
    const result = await fetchReferenceImages(
      props.record.record_id,
      props.record.note_link || '',
      props.record.images || []
    )

    if (result.success) {
      fetchMessage.value = {
        type: 'success',
        text: `✓ 成功下载 ${result.count} 张图片`
      }
      if (props.record && result.images) {
        props.record.images = result.images
      }
      setTimeout(() => fetchMessage.value = null, 3000)
    } else {
      fetchMessage.value = {
        type: 'error',
        text: result.message || '下载失败'
      }
      setTimeout(() => fetchMessage.value = null, 5000)
    }
  } catch (e) {
    fetchMessage.value = {
      type: 'error',
      text: `网络错误: ${(e as Error).message}`
    }
  } finally {
    isFetching.value = false
  }
}

// 监听记录变化
watch(() => props.record, (newRecord) => {
  if (newRecord) {
    previewImageSrc.value = ''
    fetchMessage.value = null
    hasCheckedLocal.value = false
    checkLocalImages()
  }
}, { immediate: true })
</script>

<style scoped>
/* 弹窗遮罩 */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s;
}

.modal-enter-active .modal-container,
.modal-leave-active .modal-container {
  transition: transform 0.3s, opacity 0.3s;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .modal-container,
.modal-leave-to .modal-container {
  transform: scale(0.95);
  opacity: 0;
}

/* 弹窗容器 */
.modal-container {
  background: white;
  border-radius: 16px;
  max-width: 600px;
  width: 100%;
  max-height: 90vh;
  overflow: hidden;
  position: relative;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.25);
}

/* 关闭按钮 */
.modal-close {
  position: absolute;
  top: 16px;
  right: 16px;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.5);
  border: none;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
  transition: background-color 0.2s;
}

.modal-close:hover {
  background: rgba(0, 0, 0, 0.7);
}

/* 内容区域 */
.modal-content {
  max-height: 90vh;
  overflow-y: auto;
  padding: 20px;
}

/* 封面图 */
.detail-cover {
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 20px;
}

.cover-image {
  width: 100%;
  aspect-ratio: 3/4;
  object-fit: cover;
}

.cover-gallery {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
}

.gallery-image {
  width: 100%;
  aspect-ratio: 3/4;
  object-fit: cover;
}

/* 标题 */
.detail-header {
  margin-bottom: 16px;
}

.detail-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-main, #1a1a1a);
  margin: 0 0 12px 0;
}

.detail-link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: var(--primary, #ff2442);
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
}

.detail-link:hover {
  text-decoration: underline;
}

/* 正文 */
.detail-body {
  margin-bottom: 20px;
  padding: 16px;
  background: #f9f9f9;
  border-radius: 12px;
}

.body-text {
  font-size: 14px;
  line-height: 1.8;
  color: var(--text-main, #1a1a1a);
  white-space: pre-wrap;
}

/* 博主信息 */
.detail-blogger {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: #f9f9f9;
  border-radius: 12px;
  margin-bottom: 20px;
}

.blogger-avatar,
.blogger-avatar-placeholder {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  object-fit: cover;
}

.blogger-avatar-placeholder {
  background: linear-gradient(135deg, var(--primary) 0%, #ff6b6b 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 20px;
  font-weight: 600;
}

.blogger-info {
  flex: 1;
}

.blogger-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-main, #1a1a1a);
}

.blogger-meta {
  font-size: 13px;
  color: var(--text-sub, #666);
  margin-top: 2px;
}

.blogger-link {
  padding: 8px 16px;
  border-radius: 8px;
  background: white;
  border: 1px solid #e5e5e5;
  color: var(--text-sub, #666);
  text-decoration: none;
  font-size: 13px;
  transition: all 0.2s;
}

.blogger-link:hover {
  border-color: var(--primary, #ff2442);
  color: var(--primary, #ff2442);
}

/* 互动数据 */
.detail-metrics {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 20px;
}

.metric-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 12px;
  background: #f9f9f9;
  border-radius: 8px;
}

.metric-item svg {
  color: var(--text-placeholder, #ccc);
}

.metric-item span:not(.metric-label) {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-main, #1a1a1a);
}

.metric-label {
  font-size: 12px;
  color: var(--text-sub, #666);
}

/* 标签 */
.detail-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 20px;
}

.tag {
  padding: 6px 12px;
  border-radius: 100px;
  background: #f0f0f0;
  font-size: 13px;
  color: var(--text-sub, #666);
}

/* 分类信息 */
.detail-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  padding: 16px;
  background: #f9f9f9;
  border-radius: 12px;
  margin-bottom: 20px;
}

.meta-item {
  font-size: 13px;
  color: var(--text-sub, #666);
}

.meta-label {
  font-weight: 500;
  color: var(--text-main, #1a1a1a);
}

/* 所有图片 */
.detail-images {
  margin-top: 20px;
}

.images-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-main, #1a1a1a);
  margin-bottom: 12px;
}

.images-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 8px;
}

.images-item {
  width: 100%;
  aspect-ratio: 1;
  object-fit: cover;
  border-radius: 8px;
  cursor: pointer;
  transition: transform 0.2s;
}

.images-item:hover {
  transform: scale(1.05);
}

/* 加载状态 */
.images-loading {
  text-align: center;
  padding: 40px 20px;
  color: var(--text-sub, #666);
}

/* 空状态 */
.images-empty-state {
  text-align: center;
  padding: 40px 20px;
  background: #f9f9f9;
  border-radius: 12px;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.images-empty-state h3 {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-main, #1a1a1a);
  margin: 0 0 8px 0;
}

.empty-text {
  font-size: 14px;
  color: var(--text-sub, #666);
  margin: 0 0 16px 0;
}

.empty-hint {
  font-size: 13px;
  color: var(--text-sub, #666);
  margin: 0 0 24px 0;
}

/* 路径显示框 */
.path-box {
  background: #f0f0f0;
  padding: 12px 16px;
  border-radius: 8px;
  margin: 0 auto 20px;
  max-width: 500px;
  text-align: left;
}

.path-box code {
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 13px;
  color: #333;
  word-break: break-all;
}

/* 操作按钮 */
.action-buttons {
  display: flex;
  gap: 12px;
  justify-content: center;
  flex-wrap: wrap;
}

.action-btn {
  padding: 10px 24px;
  border-radius: 8px;
  border: 1px solid #e5e5e5;
  background: white;
  color: var(--text-main, #1a1a1a);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  text-decoration: none;
  transition: all 0.2s;
  display: inline-block;
}

.action-btn:hover:not(:disabled) {
  border-color: var(--primary, #ff2442);
  color: var(--primary, #ff2442);
}

.action-btn.primary {
  background: var(--primary, #ff2442);
  border-color: var(--primary, #ff2442);
  color: white;
}

.action-btn.primary:hover:not(:disabled) {
  background: var(--primary-hover, #e61e3a);
  border-color: var(--primary-hover, #e61e3a);
}

.action-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 状态消息 */
.fetch-message {
  margin-top: 16px;
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 14px;
}

.fetch-message.success {
  background: #e8f5e9;
  color: #2e7d32;
}

.fetch-message.error {
  background: #ffebee;
  color: #c62828;
}

.fetch-message.info {
  background: #e3f2fd;
  color: #1565c0;
}

/* 加载状态 */
.modal-loading {
  padding: 60px 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #f0f0f0;
  border-top-color: var(--primary, #ff2442);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* 图片预览 */
.preview-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1100;
  padding: 40px;
}

.preview-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}
</style>
