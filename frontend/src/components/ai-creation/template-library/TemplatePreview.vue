<template>
  <div class="template-preview-modal" :class="{ visible }" @click.self="handleClose">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h3>{{ template.name }}</h3>
        <button @click="handleClose" class="close-btn">×</button>
      </div>

      <div class="modal-body">
        <div class="preview-section">
          <h4 class="section-title">模板类型</h4>
          <span class="type-badge" :class="template.type">{{ typeLabel }}</span>
        </div>

        <div class="preview-section">
          <h4 class="section-title">模板模式</h4>
          <div class="pattern-box">
            <code>{{ template.pattern }}</code>
          </div>
        </div>

        <div v-if="template.variables?.length > 0" class="preview-section">
          <h4 class="section-title">变量列表</h4>
          <div class="variables-box">
            <span
              v-for="variable in template.variables"
              :key="variable"
              class="variable-item"
            >
              <code>{{ variable }}</code>
            </span>
          </div>
        </div>

        <div v-if="template.examples?.length > 0" class="preview-section">
          <h4 class="section-title">应用示例</h4>
          <div class="examples-box">
            <div
              v-for="(example, idx) in template.examples"
              :key="idx"
              class="example-item"
            >
              {{ example }}
            </div>
          </div>
        </div>

        <div v-if="template.source_records?.length > 0" class="preview-section">
          <h4 class="section-title">来源笔记</h4>
          <div class="sources-box">
            <span
              v-for="id in template.source_records.slice(0, 3)"
              :key="id"
              class="source-item"
            >
              {{ id.slice(0, 8) }}...
            </span>
            <span v-if="template.source_records.length > 3" class="more-indicator">
              +{{ template.source_records.length - 3 }}
            </span>
          </div>
        </div>
      </div>

      <div class="modal-footer">
        <button @click="handleClose" class="btn-secondary">关闭</button>
        <button @click="handleApply" class="btn-primary">应用此模板</button>
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
  pattern: string
  variables: string[]
  source_records: string[]
  examples: string[]
}

const props = defineProps<{
  template: Template
  visible: boolean
}>()

const emit = defineEmits<{
  close: []
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

function handleClose() {
  emit('close')
}

function handleApply() {
  emit('apply', props.template)
}
</script>

<style scoped>
.template-preview-modal {
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
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.2s;
}

.template-preview-modal.visible {
  opacity: 1;
  pointer-events: all;
}

.modal-content {
  background: white;
  border-radius: 16px;
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #e8e6e3;
}

.modal-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.close-btn {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: none;
  background: #f0efed;
  color: #666;
  font-size: 20px;
  cursor: pointer;
  line-height: 1;
}

.close-btn:hover {
  background: #e0dedb;
  color: #333;
}

.modal-body {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.preview-section {
  margin-bottom: 20px;
}

.preview-section:last-child {
  margin-bottom: 0;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin: 0 0 12px 0;
}

.type-badge {
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  text-transform: uppercase;
}

.type-badge.title {
  background: rgba(52, 152, 219, 0.1);
  color: #3498db;
}

.type-badge.structure {
  background: rgba(155, 89, 182, 0.1);
  color: #9b59b6;
}

.type-badge.visual {
  background: rgba(255, 152, 0, 0.1);
  color: #ff9800;
}

.pattern-box {
  padding: 12px;
  background: #f8f7f5;
  border-radius: 8px;
  border: 1px solid #e8e6e3;
}

.pattern-box code {
  font-size: 14px;
  color: #333;
  white-space: pre-wrap;
}

.variables-box {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 12px;
  background: #f8f7f5;
  border-radius: 8px;
}

.variable-item {
  padding: 4px 8px;
  background: white;
  border: 1px solid #e8e6e3;
  border-radius: 4px;
  font-size: 13px;
}

.variable-item code {
  color: var(--primary, #ff2442);
  font-size: 12px;
}

.examples-box {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.example-item {
  padding: 8px 12px;
  background: #f8f7f5;
  border-radius: 6px;
  font-size: 13px;
  color: #333;
  border-left: 3px solid var(--primary, #ff2442);
}

.sources-box {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 12px;
  background: #f8f7f5;
  border-radius: 8px;
}

.source-item {
  padding: 4px 8px;
  background: white;
  border: 1px solid #e8e6e3;
  border-radius: 4px;
  font-size: 11px;
  color: #666;
  font-family: monospace;
}

.more-indicator {
  padding: 4px 8px;
  background: #e0dedb;
  border-radius: 4px;
  font-size: 12px;
  color: #666;
}

.modal-footer {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  padding: 16px 20px;
  border-top: 1px solid #e8e6e3;
}

.btn-secondary,
.btn-primary {
  padding: 10px 24px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary {
  border: 1px solid #e0dedb;
  background: white;
  color: #333;
}

.btn-secondary:hover {
  border-color: #666;
}

.btn-primary {
  border: none;
  background: var(--primary, #ff2442);
  color: white;
}

.btn-primary:hover {
  background: #e61f37;
}
</style>
