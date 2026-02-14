<template>
  <div class="learnable-elements">
    <div class="elements-header">
      <span class="header-icon">📚</span>
      <span class="header-title">可复用元素</span>
    </div>
    <div class="elements-grid">
      <div v-for="(value, key) in displayElements" :key="key" class="element-item">
        <span class="element-icon">{{ getElementIcon(key) }}</span>
        <div class="element-content">
          <span class="element-label">{{ getElementLabel(key) }}</span>
          <span class="element-value">{{ value }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { LearnableElements } from '@/types/recommendation'

interface Props {
  elements: LearnableElements
}

const props = defineProps<Props>()

// 过滤掉空值
const displayElements = computed(() => {
  const result: Record<string, string> = {}
  for (const [key, value] of Object.entries(props.elements)) {
    if (value && value.trim()) {
      result[key] = value
    }
  }
  return result
})

function getElementIcon(key: string): string {
  const icons: Record<string, string> = {
    hook: '🎣',
    structure: '🏗️',
    tone: '🎨',
    cta: '📢'
  }
  return icons[key] || '•'
}

function getElementLabel(key: string): string {
  const labels: Record<string, string> = {
    hook: '钩子类型',
    structure: '结构框架',
    tone: '语言风格',
    cta: '互动设计'
  }
  return labels[key] || key
}
</script>

<style scoped>
.learnable-elements {
  padding: 12px;
  background: linear-gradient(135deg, rgba(76, 175, 80, 0.03) 0%, rgba(255, 152, 0, 0.03) 100%);
  border-radius: 8px;
  border: 1px solid rgba(76, 175, 80, 0.1);
}

.elements-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 12px;
  font-size: 13px;
  font-weight: 600;
  color: #4caf50;
}

.header-icon {
  font-size: 14px;
}

.header-title {
  line-height: 1;
}

.elements-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.element-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 8px;
  background: white;
  border-radius: 6px;
  border: 1px solid #e8e6e3;
  transition: all 0.2s ease;
}

.element-item:hover {
  border-color: rgba(76, 175, 80, 0.3);
  box-shadow: 0 2px 8px rgba(76, 175, 80, 0.1);
}

.element-icon {
  flex-shrink: 0;
  font-size: 16px;
  line-height: 1;
}

.element-content {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.element-label {
  font-size: 11px;
  color: #999;
  font-weight: 500;
}

.element-value {
  font-size: 12px;
  color: #333;
  font-weight: 500;
  line-height: 1.4;
  word-break: break-all;
}
</style>
