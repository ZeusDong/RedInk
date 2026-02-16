<template>
  <div class="template-group-card">
    <!-- 头部：原笔记信息 -->
    <div class="group-header">
      <!-- 封面图 -->
      <div v-if="group.source_cover" class="group-cover">
        <img :src="group.source_cover" :alt="group.source_title" @error="handleCoverError" />
      </div>
      <div v-else class="group-cover placeholder">
        <span class="placeholder-icon">📔</span>
      </div>

      <!-- 标题和信息 -->
      <div class="group-info">
        <div class="group-title-row">
          <h3 class="group-title">{{ group.source_title }}</h3>
          <span v-if="group.source_industry" class="industry-tag">
            {{ group.source_industry }}
          </span>
        </div>
        <div class="group-meta">
          <span v-if="group.match_score !== undefined" class="match-score">
            {{ matchLevel }} ({{ formattedScore }}分)
          </span>
          <span class="saved-time">
            保存于 {{ formattedTime }}
          </span>
          <button class="view-source-btn" @click="handleViewSource">
            查看原笔记
          </button>
        </div>
      </div>

      <!-- 删除按钮 -->
      <button class="delete-group-btn" @click="handleDeleteGroup" title="删除此模板组">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="3 6 5 6 21 6"></polyline>
          <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
        </svg>
      </button>
    </div>

    <!-- 技巧列表 -->
    <div class="elements-section">
      <div class="elements-grid">
        <TemplateElementCard
          v-for="element in group.elements"
          :key="element.id"
          :element="element"
          :group-id="group.group_id"
          @preview="handlePreviewElement"
          @apply="handleApplyElement"
          @delete="handleDeleteElement"
        />
      </div>
      <div v-if="group.elements.length === 0" class="empty-elements">
        暂无技巧
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import TemplateElementCard from './TemplateElementCard.vue'
import type { TemplateGroup, TemplateElement } from '@/types/templateGroup'

interface Props {
  group: TemplateGroup
}

interface Emits {
  (e: 'delete-group', group: TemplateGroup): void
  (e: 'preview-element', element: TemplateElement): void
  (e: 'apply-element', element: TemplateElement, groupId: string): void
  (e: 'delete-element', element: TemplateElement, groupId: string): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()
const router = useRouter()

const formattedScore = computed(() => {
  if (props.group.match_score === undefined) return '-'
  return (props.group.match_score * 10).toFixed(1)
})

const matchLevel = computed(() => {
  if (props.group.match_score === undefined) return ''
  const score = props.group.match_score
  if (score >= 0.7) return '高度匹配'
  if (score >= 0.4) return '中度匹配'
  return '一般匹配'
})

const formattedTime = computed(() => {
  const savedAt = new Date(props.group.saved_at)
  const now = new Date()
  const diff = now.getTime() - savedAt.getTime()

  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes} 分钟前`
  if (hours < 24) return `${hours} 小时前`
  if (days < 7) return `${days} 天前`

  return savedAt.toLocaleDateString('zh-CN')
})

function handleCoverError(event: Event) {
  const img = event.target as HTMLImageElement
  img.style.display = 'none'
  const parent = img.parentElement
  if (parent) {
    parent.classList.add('placeholder')
    parent.innerHTML = '<span class="placeholder-icon">📔</span>'
  }
}

function handleViewSource() {
  router.push({
    name: 'HistoryDetail',
    params: { id: props.group.source_record_id }
  })
}

function handleDeleteGroup() {
  emit('delete-group', props.group)
}

function handlePreviewElement(element: TemplateElement) {
  emit('preview-element', element)
}

function handleApplyElement(element: TemplateElement) {
  emit('apply-element', element, props.group.group_id)
}

function handleDeleteElement(element: TemplateElement) {
  emit('delete-element', element, props.group.group_id)
}
</script>

<style scoped>
.template-group-card {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  margin-bottom: 20px;
  border: 1px solid #f0f0f0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.group-header {
  display: flex;
  gap: 16px;
  padding: 20px;
  border-bottom: 1px solid #f5f5f5;
  position: relative;
}

.group-cover {
  width: 80px;
  height: 80px;
  border-radius: 10px;
  overflow: hidden;
  flex-shrink: 0;
  background: #f5f5f5;
}

.group-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.group-cover.placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f5f5f5 0%, #e8e8e8 100%);
}

.placeholder-icon {
  font-size: 32px;
}

.group-info {
  flex: 1;
  min-width: 0;
}

.group-title-row {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  margin-bottom: 8px;
}

.group-title {
  font-size: 16px;
  font-weight: 700;
  color: #333;
  margin: 0;
  line-height: 1.4;
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.industry-tag {
  padding: 4px 10px;
  background: #f5f5f5;
  border-radius: 6px;
  font-size: 12px;
  color: #666;
  font-weight: 500;
  flex-shrink: 0;
}

.group-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.match-score {
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
}

.match-score:nth-of-type(1) {
  background: #e8f5e9;
  color: #2e7d32;
}

.match-score:nth-of-type(2) {
  background: #fff3e0;
  color: #e65100;
}

.match-score:nth-of-type(3) {
  background: #f5f5f5;
  color: #666;
}

.saved-time {
  font-size: 12px;
  color: #999;
}

.view-source-btn {
  padding: 4px 10px;
  border: 1px solid #e0dedb;
  border-radius: 6px;
  background: white;
  color: #666;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.view-source-btn:hover {
  border-color: var(--primary, #ff2442);
  color: var(--primary, #ff2442);
}

.delete-group-btn {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 8px;
  background: transparent;
  color: #ccc;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.delete-group-btn:hover {
  background: #ffebee;
  color: #ff5252;
}

.elements-section {
  padding: 20px;
}

.elements-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 16px;
}

.empty-elements {
  text-align: center;
  padding: 30px;
  color: #999;
  font-size: 14px;
}
</style>
