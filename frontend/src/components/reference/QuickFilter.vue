<template>
  <!-- 快捷筛选栏 -->
  <div class="quick-filter">
    <!-- 搜索框 -->
    <div class="search-box">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="11" cy="11" r="8"></circle>
        <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
      </svg>
      <input
        type="text"
        :value="filters.keyword"
        @input="$emit('update:keyword', ($event.target as HTMLInputElement).value)"
        placeholder="搜索标题、正文、标签、博主..."
        @keyup.enter="$emit('search')"
      />
    </div>

    <!-- 快捷筛选选项 -->
    <div class="quick-options">
      <!-- 行业选择 -->
      <select
        :value="filters.industry"
        @change="$emit('update:industry', ($event.target as HTMLSelectElement).value)"
        class="quick-select"
      >
        <option value="">全部行业</option>
        <option v-for="industry in availableIndustries" :key="industry" :value="industry">
          {{ industry }}
        </option>
      </select>

      <!-- 类型选择 -->
      <div class="type-toggles">
        <button
          v-for="type in typeOptions"
          :key="type.value"
          class="type-btn"
          :class="{ active: filters.note_type === type.value || (!filters.note_type && type.value === '') }"
          @click="$emit('update:noteType', type.value)"
        >
          {{ type.label }}
        </button>
      </div>

      <!-- 高级筛选按钮 -->
      <button
        class="advanced-toggle"
        :class="{ active: showAdvanced }"
        @click="$emit('toggle:advanced')"
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="3"></circle>
          <path d="M12 1v6m0 6v6m9-9h-6m-6 0H3m14.74 7.26l-4.24 4.24M6.26 6.26l4.24 4.24"></path>
        </svg>
        高级筛选
        <svg class="chevron" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline :points="showAdvanced ? '18 15 12 9 6 15' : '6 9 12 15 18 9'"></polyline>
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { ReferenceFilterState } from '@/stores/reference'

/**
 * 快捷筛选栏组件
 *
 * 提供关键词搜索、行业、类型等常用筛选功能
 */

// 定义 Props
const props = defineProps<{
  filters: ReferenceFilterState
  availableIndustries: string[]
  showAdvanced: boolean
}>()

// 定义 Emits
defineEmits<{
  (e: 'update:keyword', value: string): void
  (e: 'update:industry', value: string): void
  (e: 'update:noteType', value: string): void
  (e: 'toggle:advanced'): void
  (e: 'search'): void
}>()

// 类型选项
const typeOptions = [
  { label: '全部类型', value: '' },
  { label: '图文', value: '图文' },
  { label: '视频', value: '视频' }
]
</script>

<style scoped>
.quick-filter {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 0;
  background: transparent;
  border: none;
}

/* 搜索框 */
.search-box {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 11px 14px;
  background: #f8f7f5;
  border-radius: 10px;
  transition: all 0.2s;
  border: 1px solid transparent;
}

.search-box:focus-within {
  background: white;
  border-color: var(--primary, #ff2442);
  box-shadow: 0 0 0 3px rgba(255, 36, 66, 0.1);
}

.search-box svg {
  color: #bbb;
  flex-shrink: 0;
}

.search-box input {
  flex: 1;
  background: none;
  border: none;
  outline: none;
  font-size: 13px;
  color: #1a1a1a;
}

.search-box input::placeholder {
  color: #bbb;
}

/* 快捷选项区 */
.quick-options {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

/* 下拉选择 */
.quick-select {
  width: 100%;
  padding: 10px 32px 10px 12px;
  border: 1px solid #e0dedb;
  border-radius: 8px;
  background: white;
  font-size: 13px;
  color: #1a1a1a;
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%23666' stroke-width='2.5'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 10px center;
  transition: border-color 0.2s;
}

.quick-select:hover {
  border-color: #ccc;
}

.quick-select:focus {
  outline: none;
  border-color: var(--primary, #ff2442);
  box-shadow: 0 0 0 3px rgba(255, 36, 66, 0.1);
}

/* 类型切换按钮 */
.type-toggles {
  display: flex;
  background: #f0efed;
  border-radius: 8px;
  padding: 3px;
}

.type-btn {
  flex: 1;
  padding: 8px;
  border: none;
  border-radius: 6px;
  background: transparent;
  font-size: 12px;
  font-weight: 500;
  color: #666;
  cursor: pointer;
  transition: all 0.2s;
  text-align: center;
}

.type-btn:hover {
  color: #333;
}

.type-btn.active {
  background: white;
  color: var(--primary, #ff2442);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

/* 高级筛选按钮 */
.advanced-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 11px 16px;
  border: 1px solid #e0dedb;
  border-radius: 8px;
  background: white;
  font-size: 13px;
  font-weight: 600;
  color: #666;
  cursor: pointer;
  transition: all 0.2s;
  width: 100%;
}

.advanced-toggle:hover {
  border-color: var(--primary, #ff2442);
  color: var(--primary, #ff2442);
}

.advanced-toggle.active {
  background: var(--primary, #ff2442);
  border-color: var(--primary, #ff2442);
  color: white;
}

.advanced-toggle svg {
  flex-shrink: 0;
}

.advanced-toggle .chevron {
  transition: transform 0.2s;
}

.advanced-toggle.active .chevron {
  transform: rotate(180deg);
}
</style>
