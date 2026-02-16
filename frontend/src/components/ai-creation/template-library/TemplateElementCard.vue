<template>
  <div class="template-element-card">
    <!-- 技巧类型标签 -->
    <div class="element-header">
      <span :class="['element-type', `type-${element.type}`]">
        {{ typeLabel }}
      </span>
      <span v-if="element.usage_count > 0" class="usage-badge">
        已用 {{ element.usage_count }}
      </span>
    </div>

    <!-- 技巧名称 -->
    <h4 class="element-name">{{ element.name }}</h4>

    <!-- 技巧描述 -->
    <p class="element-description">{{ element.description }}</p>

    <!-- 技巧内容预览 -->
    <div class="element-content-preview">
      {{ truncateContent }}
    </div>

    <!-- 操作按钮 -->
    <div class="element-actions">
      <button class="action-btn preview-btn" @click="handlePreview">
        预览
      </button>
      <button class="action-btn apply-btn" @click="handleApply">
        应用
      </button>
      <button class="action-btn delete-btn" @click="handleDelete">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="3 6 5 6 21 6"></polyline>
          <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { TemplateElement } from '@/types/templateGroup'

interface Props {
  element: TemplateElement
  groupId: string
}

interface Emits {
  (e: 'preview', element: TemplateElement): void
  (e: 'apply', element: TemplateElement): void
  (e: 'delete', element: TemplateElement): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const typeLabel = computed(() => {
  const labels: Record<string, string> = {
    title: '标题技巧',
    structure: '结构技巧',
    tone: '风格技巧',
    cta: '互动技巧'
  }
  return labels[props.element.type] || props.element.type
})

const truncateContent = computed(() => {
  const content = props.element.content
  if (content.length > 50) {
    return content.slice(0, 50) + '...'
  }
  return content
})

function handlePreview() {
  emit('preview', props.element)
}

function handleApply() {
  emit('apply', props.element)
}

function handleDelete() {
  emit('delete', props.element)
}
</script>

<style scoped>
.template-element-card {
  display: flex;
  flex-direction: column;
  padding: 16px;
  background: #fafafa;
  border-radius: 10px;
  border: 1px solid #f0f0f0;
  transition: all 0.2s;
}

.template-element-card:hover {
  background: #f5f5f5;
  border-color: #e0e0e0;
}

.element-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.element-type {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
}

.type-title {
  background: #fff3e0;
  color: #e65100;
}

.type-structure {
  background: #e3f2fd;
  color: #1565c0;
}

.type-tone {
  background: #f3e5f5;
  color: #7b1fa2;
}

.type-cta {
  background: #e8f5e9;
  color: #2e7d32;
}

.usage-badge {
  font-size: 11px;
  color: #999;
}

.element-name {
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin: 0 0 6px 0;
}

.element-description {
  font-size: 12px;
  color: #666;
  margin: 0 0 10px 0;
  line-height: 1.4;
}

.element-content-preview {
  flex: 1;
  font-size: 12px;
  color: #888;
  padding: 10px;
  background: white;
  border-radius: 6px;
  margin-bottom: 12px;
  line-height: 1.5;
  font-family: 'PingFang SC', -apple-system, BlinkMacSystemFont, sans-serif;
}

.element-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #e0dedb;
  border-radius: 6px;
  background: white;
  color: #666;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

.action-btn:hover {
  border-color: #ccc;
  background: #fafafa;
}

.apply-btn {
  border-color: var(--primary, #ff2442);
  color: var(--primary, #ff2442);
}

.apply-btn:hover {
  background: var(--primary, #ff2442);
  color: white;
}

.delete-btn {
  flex: 0 0 auto;
  width: 32px;
  padding: 8px;
  color: #999;
}

.delete-btn:hover {
  border-color: #ff5252;
  color: #ff5252;
  background: #ffebee;
}
</style>
