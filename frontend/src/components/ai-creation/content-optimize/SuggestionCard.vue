<template>
  <div class="suggestion-card" :class="[`severity-${suggestion.severity}`, { applied: suggestion.applied }]">
    <div class="card-header">
      <div class="severity-badge" :class="suggestion.severity">
        {{ severityIcon }}
        {{ severityLabel }}
      </div>
      <div class="card-actions">
        <button
          v-if="!suggestion.applied && canApply"
          @click="handleApply"
          class="action-btn apply"
          title="应用此建议"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="20 6 9 17 4 18"></polyline>
          </svg>
          应用
        </button>
        <button
          v-if="suggestion.applied"
          @click="handleRevert"
          class="action-btn revert"
          title="撤销此建议"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="4 12 20 12"></polyline>
          </svg>
          已应用
        </button>
        <button
          @click="handleDismiss"
          class="action-btn dismiss"
          title="忽略此建议"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18"></line>
          </svg>
        </button>
      </div>
    </div>

    <div class="card-body">
      <h5 class="suggestion-title">{{ suggestion.message }}</h5>

      <p v-if="suggestion.detail" class="suggestion-detail">
        {{ suggestion.detail }}
      </p>

      <!-- 操作建议详情 -->
      <div v-if="suggestion.action_data" class="action-details">
        <span class="action-label">建议操作：</span>
        <code class="action-code">{{ getActionLabel() }}</code>

        <div v-if="suggestion.reference_record" class="reference-info">
          <span class="reference-label">参考笔记：</span>
          <a
            href="#"
            @click.prevent="handleViewReference"
            class="reference-link"
          >
            {{ suggestion.reference_record.title }}
          </a>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Suggestion {
  id: string
  type: 'title' | 'structure' | 'visual' | 'engagement'
  severity: 'critical' | 'warning' | 'info' | 'success'
  message: string
  detail?: string
  action_type: 'edit' | 'insert' | 'replace' | 'reference'
  action_data?: any
  reference_record?: {
    id: string
    title: string
    url?: string
  }
  applied: boolean
}

const props = defineProps<{
  suggestion: Suggestion
}>()

const emit = defineEmits<{
  apply: [suggestion: Suggestion]
  revert: [suggestion: Suggestion]
  dismiss: [suggestion: Suggestion]
  viewReference: [record: any]
}>()

const severityIcon = computed(() => {
  const icons = {
    critical: '⛔',
    warning: '⚠️',
    info: 'ℹ️',
    success: '✅'
  }
  return icons[props.suggestion.severity] || '•'
})

const severityLabel = computed(() => {
  const labels = {
    critical: '严重问题',
    warning: '需要改进',
    info: '优化建议',
    success: '已完成'
  }
  return labels[props.suggestion.severity] || '未知'
})

const canApply = computed(() => {
  return !props.suggestion.applied && props.suggestion.action_type
})

function getActionLabel(): string {
  const type = props.suggestion.action_type
  const labels = {
    edit: '编辑内容',
    insert: '插入内容',
    replace: '替换内容',
    reference: '参考笔记'
  }
  return labels[type] || type
}

function handleApply() {
  emit('apply', props.suggestion)
}

function handleRevert() {
  emit('revert', props.suggestion)
}

function handleDismiss() {
  emit('dismiss', props.suggestion)
}

function handleViewReference() {
  if (props.suggestion.reference_record) {
    emit('viewReference', props.suggestion.reference_record)
  }
}
</script>

<style scoped>
.suggestion-card {
  background: white;
  border: 1px solid #e8e6e3;
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.2s;
}

.suggestion-card:hover {
  border-color: var(--primary, #ff2442);
}

.suggestion-card.applied {
  opacity: 0.6;
  background: #f8f7f5;
}

.suggestion-card.severity-critical {
  border-left: 4px solid #ff2442;
}

.suggestion-card.severity-warning {
  border-left: 4px solid #ffa500;
}

.suggestion-card.severity-info {
  border-left: 4px solid #3498db;
}

.suggestion-card.severity-success {
  border-left: 4px solid #10b981;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f8f7f5;
  border-bottom: 1px solid #e8e6e3;
}

.severity-badge {
  padding: 4px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
}

.severity-badge.critical {
  background: rgba(255, 36, 66, 0.1);
  color: #ff2442;
}

.severity-badge.warning {
  background: rgba(255, 165, 0, 0.1);
  color: #ffa500;
}

.severity-badge.info {
  background: rgba(52, 152, 219, 0.1);
  color: #3498db;
}

.severity-badge.success {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.card-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
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

.action-btn:hover {
  border-color: var(--primary, #ff2442);
  color: var(--primary, #ff2442);
}

.action-btn.apply {
  border-color: var(--primary, #ff2442);
  background: rgba(255, 36, 66, 0.1);
  color: #ff2442;
}

.action-btn.revert {
  border-color: #ffa500;
  color: #ffa500;
}

.card-body {
  padding: 16px;
}

.suggestion-title {
  font-size: 15px;
  font-weight: 600;
  color: #333;
  margin: 0 0 12px 0;
}

.suggestion-detail {
  font-size: 14px;
  color: #666;
  line-height: 1.5;
  margin: 0 0 12px 0;
}

.action-details {
  margin-top: 12px;
  padding: 12px;
  background: #f8f7f5;
  border-radius: 8px;
}

.action-label {
  font-size: 12px;
  color: #666;
  display: block;
  margin-bottom: 6px;
}

.action-code {
  font-size: 13px;
  color: #333;
  background: white;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: monospace;
}

.reference-info {
  margin-top: 8px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.reference-label {
  font-size: 12px;
  color: #666;
}

.reference-link {
  font-size: 13px;
  color: var(--primary, #ff2442);
  text-decoration: none;
}

.reference-link:hover {
  text-decoration: underline;
}
</style>
