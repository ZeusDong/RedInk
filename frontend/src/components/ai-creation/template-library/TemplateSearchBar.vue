<template>
  <div class="template-search-bar">
    <!-- 搜索框 -->
    <div class="search-box">
      <svg class="search-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="11" cy="11" r="8"></circle>
        <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
      </svg>
      <input
        v-model="localSearchQuery"
        type="text"
        placeholder="搜索技巧或笔记..."
        class="search-input"
        @input="handleSearchInput"
      />
    </div>

    <!-- 类型筛选 -->
    <div class="filter-buttons">
      <button
        v-for="type in typeOptions"
        :key="type.value"
        :class="['filter-btn', { active: localSelectedType === type.value }]"
        @click="handleTypeSelect(type.value)"
      >
        {{ type.label }}
      </button>
    </div>

    <!-- 排序 -->
    <div class="sort-box">
      <span class="sort-label">排序:</span>
      <select v-model="localSortBy" class="sort-select" @change="handleSortChange">
        <option v-for="option in sortOptions" :key="option.value" :value="option.value">
          {{ option.label }}
        </option>
      </select>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useTemplateGroupStore } from '@/stores/templateGroup'
import type { TemplateElementType } from '@/types/templateGroup'

interface TypeOption {
  value: 'all' | TemplateElementType
  label: string
}

interface SortOption {
  value: 'saved_at' | 'usage_count' | 'match_score'
  label: string
}

const templateGroupStore = useTemplateGroupStore()

// 本地状态，用于防抖
const localSearchQuery = ref(templateGroupStore.searchQuery)
const localSelectedType = ref<'all' | TemplateElementType>(templateGroupStore.selectedType)
const localSortBy = ref<'saved_at' | 'usage_count' | 'match_score'>(templateGroupStore.sortBy)

// 类型选项
const typeOptions: TypeOption[] = [
  { value: 'all', label: '全部' },
  { value: 'title', label: '标题' },
  { value: 'structure', label: '结构' },
  { value: 'tone', label: '风格' },
  { value: 'cta', label: '互动' }
]

// 排序选项
const sortOptions: SortOption[] = [
  { value: 'saved_at', label: '最新保存' },
  { value: 'usage_count', label: '使用次数' },
  { value: 'match_score', label: '匹配分数' }
]

// 搜索防抖
let searchDebounceTimer: ReturnType<typeof setTimeout> | null = null

function handleSearchInput() {
  if (searchDebounceTimer) {
    clearTimeout(searchDebounceTimer)
  }
  searchDebounceTimer = setTimeout(() => {
    templateGroupStore.setSearchQuery(localSearchQuery.value)
  }, 300)
}

function handleTypeSelect(type: 'all' | TemplateElementType) {
  localSelectedType.value = type
  templateGroupStore.setTypeFilter(type)
}

function handleSortChange() {
  templateGroupStore.setSortBy(localSortBy.value)
}

// 同步 store 状态到本地
watch(
  () => templateGroupStore.searchQuery,
  (val) => {
    localSearchQuery.value = val
  }
)

watch(
  () => templateGroupStore.selectedType,
  (val) => {
    localSelectedType.value = val
  }
)

watch(
  () => templateGroupStore.sortBy,
  (val) => {
    localSortBy.value = val
  }
)
</script>

<style scoped>
.template-search-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  align-items: center;
  padding: 16px;
  background: white;
  border-radius: 12px;
  margin-bottom: 20px;
}

.search-box {
  position: relative;
  flex: 1;
  min-width: 200px;
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #999;
}

.search-input {
  width: 100%;
  padding: 10px 12px 10px 40px;
  border: 1px solid #e0dedb;
  border-radius: 8px;
  font-size: 14px;
  color: #333;
  background: #fafafa;
  transition: all 0.2s;
}

.search-input:focus {
  outline: none;
  border-color: var(--primary, #ff2442);
  background: white;
}

.filter-buttons {
  display: flex;
  gap: 8px;
}

.filter-btn {
  padding: 8px 16px;
  border: 1px solid #e0dedb;
  border-radius: 8px;
  background: white;
  color: #666;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.filter-btn:hover {
  border-color: #ccc;
  background: #fafafa;
}

.filter-btn.active {
  border-color: var(--primary, #ff2442);
  background: var(--primary, #ff2442);
  color: white;
}

.sort-box {
  display: flex;
  align-items: center;
  gap: 8px;
}

.sort-label {
  font-size: 13px;
  color: #666;
  font-weight: 500;
}

.sort-select {
  padding: 8px 12px;
  border: 1px solid #e0dedb;
  border-radius: 8px;
  background: white;
  font-size: 13px;
  color: #333;
  cursor: pointer;
}

.sort-select:focus {
  outline: none;
  border-color: var(--primary, #ff2442);
}

@media (max-width: 768px) {
  .template-search-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-buttons {
    justify-content: center;
    flex-wrap: wrap;
  }

  .sort-box {
    justify-content: center;
  }
}
</style>
