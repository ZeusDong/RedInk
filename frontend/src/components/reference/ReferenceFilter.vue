<template>
  <!-- 对标文案筛选侧边栏 -->
  <div class="reference-filter">
    <div class="filter-header">
      <h3>筛选条件</h3>
      <button v-if="hasActiveFilters" class="clear-btn" @click="$emit('reset')">
        清空
      </button>
    </div>

    <!-- 搜索 -->
    <div class="filter-section">
      <label class="filter-label">关键词搜索</label>
      <div class="search-input">
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
    </div>

    <!-- 行业筛选 -->
    <div class="filter-section">
      <label class="filter-label">行业分类</label>
      <select
        :value="filters.industry"
        @change="$emit('update:industry', ($event.target as HTMLSelectElement).value)"
      >
        <option value="">全部行业</option>
        <option v-for="industry in availableIndustries" :key="industry" :value="industry">
          {{ industry }}
        </option>
      </select>
    </div>

    <!-- 笔记类型 -->
    <div class="filter-section">
      <label class="filter-label">笔记类型</label>
      <div class="type-options">
        <button
          v-for="type in ['图文', '视频']"
          :key="type"
          class="type-option"
          :class="{ active: filters.note_type === type }"
          @click="$emit('update:noteType', filters.note_type === type ? '' : type)"
        >
          {{ type }}
        </button>
      </div>
    </div>

    <!-- 点赞数筛选 -->
    <div class="filter-section">
      <label class="filter-label">最小点赞数</label>
      <div class="range-input">
        <input
          type="number"
          :value="filters.min_likes || ''"
          @input="$emit('update:minLikes', ($event.target as HTMLInputElement).value ? Number(($event.target as HTMLInputElement).value) : undefined)"
          placeholder="不限制"
          min="0"
        />
      </div>
      <div class="range-presets">
        <button
          v-for="preset in [1000, 5000, 10000]"
          :key="preset"
          class="preset-btn"
          @click="$emit('update:minLikes', preset)"
        >
          {{ preset >= 1000 ? preset / 1000 + 'k' : preset }}+
        </button>
      </div>
    </div>

    <!-- 收藏数筛选 -->
    <div class="filter-section">
      <label class="filter-label">最小收藏数</label>
      <div class="range-input">
        <input
          type="number"
          :value="filters.min_saves || ''"
          @input="$emit('update:minSaves', ($event.target as HTMLInputElement).value ? Number(($event.target as HTMLInputElement).value) : undefined)"
          placeholder="不限制"
          min="0"
        />
      </div>
      <div class="range-presets">
        <button
          v-for="preset in [500, 1000, 5000]"
          :key="preset"
          class="preset-btn"
          @click="$emit('update:minSaves', preset)"
        >
          {{ preset >= 1000 ? preset / 1000 + 'k' : preset }}+
        </button>
      </div>
    </div>

    <!-- 排序选项 -->
    <div class="filter-section">
      <label class="filter-label">排序方式</label>
      <div class="sort-options">
        <select
          :value="filters.sort_by"
          @change="$emit('update:sortBy', ($event.target as HTMLSelectElement).value)"
        >
          <option value="created_at">最新发布</option>
          <option value="likes">点赞最多</option>
          <option value="saves">收藏最多</option>
          <option value="comments">评论最多</option>
          <option value="total_engagement">总互动量</option>
          <option value="save_ratio">收藏互动比</option>
        </select>
        <button
          class="sort-order"
          :class="{ desc: filters.sort_order === 'desc' }"
          @click="$emit('toggleSortOrder')"
          :title="filters.sort_order === 'desc' ? '降序' : '升序'"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <polyline points="19 12 12 19 5 12"></polyline>
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { ReferenceFilterState } from '@/stores/reference'

/**
 * 对标文案筛选组件
 *
 * 提供关键词搜索、行业筛选、类型筛选、数值范围筛选和排序功能
 */

// 定义 Props
const props = defineProps<{
  filters: ReferenceFilterState
  availableIndustries: string[]
}>()

// 定义 Emits
defineEmits<{
  (e: 'update:keyword', value: string): void
  (e: 'update:industry', value: string): void
  (e: 'update:noteType', value: string): void
  (e: 'update:minLikes', value?: number): void
  (e: 'update:minSaves', value?: number): void
  (e: 'update:sortBy', value: string): void
  (e: 'toggleSortOrder'): void
  (e: 'search'): void
  (e: 'reset'): void
}>()

// 计算是否有活跃的筛选条件
const hasActiveFilters = computed(() => {
  return !!(
    props.filters.keyword ||
    props.filters.industry ||
    props.filters.note_type ||
    props.filters.min_likes !== undefined ||
    props.filters.min_saves !== undefined
  )
})
</script>

<style scoped>
.reference-filter {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.filter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filter-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-main, #1a1a1a);
  margin: 0;
}

.clear-btn {
  background: none;
  border: none;
  color: var(--primary, #ff2442);
  font-size: 13px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.clear-btn:hover {
  background: rgba(255, 36, 66, 0.1);
}

.filter-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.filter-label {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-sub, #666);
}

/* 搜索输入 */
.search-input {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  background: #f5f5f5;
  border-radius: 8px;
  transition: background-color 0.2s;
}

.search-input:focus-within {
  background: #fff;
  box-shadow: 0 0 0 2px var(--primary, #ff2442);
}

.search-input svg {
  color: var(--text-placeholder, #ccc);
  flex-shrink: 0;
}

.search-input input {
  flex: 1;
  background: none;
  border: none;
  outline: none;
  font-size: 14px;
  color: var(--text-main, #1a1a1a);
}

.search-input input::placeholder {
  color: var(--text-placeholder, #ccc);
}

/* 下拉选择 */
select,
.range-input input {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid #e5e5e5;
  border-radius: 8px;
  background: white;
  font-size: 14px;
  color: var(--text-main, #1a1a1a);
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
}

select:focus,
.range-input input:focus {
  border-color: var(--primary, #ff2442);
  box-shadow: 0 0 0 2px rgba(255, 36, 66, 0.1);
}

.range-input input {
  margin-bottom: 8px;
}

.range-input input::placeholder {
  color: var(--text-placeholder, #ccc);
}

/* 快捷选择按钮 */
.range-presets {
  display: flex;
  gap: 8px;
}

.preset-btn {
  padding: 6px 12px;
  border: 1px solid #e5e5e5;
  border-radius: 6px;
  background: white;
  font-size: 12px;
  color: var(--text-sub, #666);
  cursor: pointer;
  transition: all 0.2s;
}

.preset-btn:hover {
  border-color: var(--primary, #ff2442);
  color: var(--primary, #ff2442);
}

/* 类型选项 */
.type-options {
  display: flex;
  gap: 8px;
}

.type-option {
  flex: 1;
  padding: 10px;
  border: 1px solid #e5e5e5;
  border-radius: 8px;
  background: white;
  font-size: 14px;
  color: var(--text-sub, #666);
  cursor: pointer;
  transition: all 0.2s;
}

.type-option:hover {
  border-color: var(--primary, #ff2442);
  color: var(--primary, #ff2442);
}

.type-option.active {
  border-color: var(--primary, #ff2442);
  background: var(--primary, #ff2442);
  color: white;
}

/* 排序选项 */
.sort-options {
  display: flex;
  gap: 8px;
}

.sort-options select {
  flex: 1;
}

.sort-order {
  padding: 10px 14px;
  border: 1px solid #e5e5e5;
  border-radius: 8px;
  background: white;
  color: var(--text-sub, #666);
  cursor: pointer;
  transition: all 0.2s;
}

.sort-order:hover {
  border-color: var(--primary, #ff2442);
  color: var(--primary, #ff2442);
}

.sort-order svg {
  transition: transform 0.2s;
}

.sort-order.desc svg {
  transform: rotate(180deg);
}
</style>
