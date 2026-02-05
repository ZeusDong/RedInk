<template>
  <div class="source-segmented-control">
    <button
      v-for="(config, key) in workspaceConfigs"
      :key="key"
      class="segment-btn"
      :class="{ active: modelValue === key }"
      @click="$emit('update:modelValue', key)"
    >
      <span class="segment-icon">{{ config.icon }}</span>
      <span class="segment-label">{{ config.label }}</span>
      <span class="segment-count">({{ counts[key] ?? '-' }})</span>
    </button>
  </div>
</template>

<script setup lang="ts" generic="K extends string">
interface Props {
  modelValue: K
  counts: Record<string, number | undefined>
}

defineProps<Props>()

defineEmits<{
  'update:modelValue': [value: K]
}>()

const workspaceConfigs: Record<string, { label: string; icon: string }> = {
  benchmark: { label: '对标账号库', icon: '🔴' },
  search: { label: '关键词搜索', icon: '🔍' }
}
</script>

<style scoped>
.source-segmented-control {
  display: inline-flex;
  background: #f0efed;
  border-radius: 10px;
  padding: 4px;
  gap: 2px;
}

.segment-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border: none;
  background: transparent;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  color: #666;
  cursor: pointer;
  transition: all 0.2s;
}

.segment-btn:hover {
  color: #333;
}

.segment-btn.active {
  background: white;
  color: var(--primary, #ff2442);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.segment-icon {
  font-size: 14px;
}

.segment-count {
  font-size: 11px;
  color: #999;
}

.segment-btn.active .segment-count {
  color: var(--primary, #ff2442);
}
</style>
