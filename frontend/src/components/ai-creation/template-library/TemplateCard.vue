<template>
  <div class="template-card" @click="handleClick">
    <div class="card-header">
      <span class="template-type" :class="typeClass">{{ typeLabel }}</span>
      <div class="card-actions">
        <button @click.stop="handlePreview" class="icon-btn" title="预览">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M1 12s4-8 4-4-4 4-4 4 4 4 14 0 6-6-6"></path>
          </svg>
        </button>
        <button @click.stop="handleApply" class="icon-btn primary" title="应用">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="20 6 9 17 4 18"></polyline>
          </svg>
        </button>
      </div>
    </div>

    <div class="card-body">
      <h4 class="template-name">{{ template.name }}</h4>
      <p class="template-description">{{ template.description || '暂无描述' }}</p>

      <!-- 模板变量 -->
      <div v-if="template.variables?.length > 0" class="variables-section">
        <span class="variables-label">变量：</span>
        <div class="variables-list">
          <span
            v-for="variable in template.variables"
            :key="variable"
            class="variable-tag"
          >
            {{ variable }}
          </span>
        </div>
      </div>

      <!-- 使用统计 -->
      <div class="stats-section">
        <span class="stat-item">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
            <polyline points="14 2 14 8 20 8"></polyline>
          </svg>
          {{ template.usage_count || 0 }} 次使用
        </span>
        <span v-if="template.industry" class="stat-item industry">
          {{ template.industry }}
        </span>
      </div>

      <!-- 示例 -->
      <div v-if="template.examples?.length > 0" class="examples-section">
        <span class="examples-label">示例：</span>
        <div class="examples-list">
          <div
            v-for="(example, idx) in template.examples.slice(0, 2)"
            :key="idx"
            class="example-item"
          >
            {{ example }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Template {
  id: string
  type: 'title' | 'structure' | 'visual'
  name: string
  industry?: string
  pattern: string
  variables: string[]
  usage_count: number
  description?: string
  examples: string[]
}

const props = defineProps<{
  template: Template
}>()

const emit = defineEmits<{
  click: [template: Template]
  preview: [template: Template]
  apply: [template: Template]
}>()

const typeLabel = computed(() => {
  const labels = {
    title: '标题模板',
    structure: '结构模板',
    visual: '视觉模板'
  }
  return labels[props.template.type] || '未知类型'
})

const typeClass = computed(() => {
  return props.template.type
})

function handleClick() {
  emit('click', props.template)
}

function handlePreview() {
  emit('preview', props.template)
}

function handleApply() {
  emit('apply', props.template)
}
</script>

<style scoped>
.template-card {
  background: white;
  border: 1px solid #e8e6e3;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.2s;
}

.template-card:hover {
  border-color: var(--primary, #ff2442);
  box-shadow: 0 4px 16px rgba(255, 36, 66, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f8f7f5;
  border-bottom: 1px solid #e8e6e3;
}

.template-type {
  padding: 4px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
}

.template-type.title {
  background: rgba(52, 152, 219, 0.1);
  color: #3498db;
}

.template-type.structure {
  background: rgba(155, 89, 182, 0.1);
  color: #9b59b6;
}

.template-type.visual {
  background: rgba(255, 152, 0, 0.1);
  color: #ff9800;
}

.card-actions {
  display: flex;
  gap: 8px;
}

.icon-btn {
  width: 32px;
  height: 32px;
  border-radius: 6px;
  border: 1px solid #e0dedb;
  background: white;
  color: #666;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.icon-btn:hover {
  border-color: var(--primary, #ff2442);
  color: var(--primary, #ff2442);
}

.icon-btn.primary {
  border-color: var(--primary, #ff2442);
  background: rgba(255, 36, 66, 0.1);
  color: var(--primary, #ff2442);
}

.card-body {
  padding: 16px;
}

.template-name {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin: 0 0 8px 0;
}

.template-description {
  font-size: 13px;
  color: #666;
  line-height: 1.5;
  margin: 0 0 12px 0;
}

.variables-section {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.variables-label {
  font-size: 12px;
  color: #666;
}

.variables-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.variable-tag {
  padding: 3px 8px;
  background: rgba(255, 36, 66, 0.1);
  color: var(--primary, #ff2442);
  border-radius: 4px;
  font-family: monospace;
  font-size: 11px;
}

.stats-section {
  display: flex;
  gap: 16px;
  padding-top: 12px;
  border-top: 1px solid #f0efed;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #666;
}

.stat-item.industry {
  padding: 2px 8px;
  background: #f0efed;
  border-radius: 4px;
}

.examples-section {
  margin-top: 12px;
}

.examples-label {
  font-size: 12px;
  color: #666;
  display: block;
  margin-bottom: 6px;
}

.examples-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.example-item {
  font-size: 12px;
  color: #333;
  padding: 6px 10px;
  background: #f8f7f5;
  border-radius: 4px;
  border-left: 2px solid var(--primary, #ff2442);
}
</style>
