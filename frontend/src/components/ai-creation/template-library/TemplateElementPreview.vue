<template>
  <div v-if="visible" class="template-element-preview-overlay" @click.self="handleClose">
    <div class="preview-modal">
      <!-- 头部 -->
      <div class="preview-header">
        <div class="header-left">
          <span :class="['element-type', `type-${element?.type}`]">
            {{ typeLabel }}
          </span>
          <h3 class="preview-title">{{ element?.name }}</h3>
        </div>
        <button class="close-btn" @click="handleClose">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>

      <!-- 内容 -->
      <div v-if="element" class="preview-content">
        <!-- 描述 -->
        <div class="section">
          <h4 class="section-title">技巧描述</h4>
          <p class="section-text">{{ element.description }}</p>
        </div>

        <!-- 具体内容 -->
        <div class="section">
          <h4 class="section-title">技巧内容</h4>
          <div class="content-box">
            <pre class="content-text">{{ element.content }}</pre>
          </div>
        </div>

        <!-- 示例 -->
        <div v-if="element.examples && element.examples.length > 0" class="section">
          <h4 class="section-title">示例</h4>
          <div class="examples-list">
            <div v-for="(example, index) in element.examples" :key="index" class="example-item">
              <span class="example-index">{{ index + 1 }}.</span>
              <span class="example-text">{{ example }}</span>
            </div>
          </div>
        </div>

        <!-- 使用统计 -->
        <div class="usage-info">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
            <circle cx="12" cy="12" r="3"></circle>
          </svg>
          <span>已使用 {{ element.usage_count }} 次</span>
        </div>
      </div>

      <!-- 底部操作 -->
      <div class="preview-footer">
        <button class="btn-cancel" @click="handleClose">
          关闭
        </button>
        <button class="btn-apply" @click="handleApply">
          应用此技巧
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { TemplateElement } from '@/types/templateGroup'

interface Props {
  element: TemplateElement | null
  groupId: string | null
  visible: boolean
}

interface Emits {
  (e: 'close'): void
  (e: 'apply', element: TemplateElement, groupId: string | null): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const typeLabel = computed(() => {
  if (!props.element) return ''
  const labels: Record<string, string> = {
    title: '标题技巧',
    structure: '结构技巧',
    tone: '风格技巧',
    cta: '互动技巧'
  }
  return labels[props.element.type] || props.element.type
})

function handleClose() {
  emit('close')
}

function handleApply() {
  if (props.element) {
    emit('apply', props.element, props.groupId)
  }
}
</script>

<style scoped>
.template-element-preview-overlay {
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

.preview-modal {
  background: white;
  border-radius: 16px;
  width: 100%;
  max-width: 560px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 20px 24px;
  border-bottom: 1px solid #f0f0f0;
}

.header-left {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.element-type {
  display: inline-flex;
  align-self: flex-start;
  padding: 4px 12px;
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

.preview-title {
  font-size: 20px;
  font-weight: 700;
  color: #333;
  margin: 0;
}

.close-btn {
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 8px;
  background: #f5f5f5;
  color: #666;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.close-btn:hover {
  background: #e0e0e0;
  color: #333;
}

.preview-content {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.section {
  margin-bottom: 24px;
}

.section-title {
  font-size: 13px;
  font-weight: 600;
  color: #999;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin: 0 0 8px 0;
}

.section-text {
  font-size: 14px;
  color: #333;
  line-height: 1.6;
  margin: 0;
}

.content-box {
  background: #fafafa;
  border-radius: 10px;
  padding: 16px;
  border: 1px solid #f0f0f0;
}

.content-text {
  font-size: 14px;
  color: #333;
  line-height: 1.7;
  margin: 0;
  white-space: pre-wrap;
  font-family: 'PingFang SC', -apple-system, BlinkMacSystemFont, sans-serif;
}

.examples-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.example-item {
  display: flex;
  gap: 10px;
  padding: 12px 16px;
  background: #fafafa;
  border-radius: 8px;
  border: 1px solid #f0f0f0;
}

.example-index {
  font-size: 13px;
  font-weight: 600;
  color: var(--primary, #ff2442);
}

.example-text {
  flex: 1;
  font-size: 14px;
  color: #333;
  line-height: 1.5;
}

.usage-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: #f5f5f5;
  border-radius: 8px;
  color: #666;
  font-size: 13px;
}

.preview-footer {
  display: flex;
  gap: 12px;
  padding: 20px 24px;
  border-top: 1px solid #f0f0f0;
}

.btn-cancel,
.btn-apply {
  flex: 1;
  padding: 12px 24px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-cancel {
  border: 1px solid #e0dedb;
  background: white;
  color: #666;
}

.btn-cancel:hover {
  background: #f5f5f5;
}

.btn-apply {
  border: none;
  background: var(--primary, #ff2442);
  color: white;
}

.btn-apply:hover {
  background: #e61f37;
}
</style>
