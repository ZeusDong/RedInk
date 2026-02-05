<template>
  <!-- 高级筛选面板 -->
  <transition name="slide-down">
    <div v-if="visible" class="advanced-filter">
      <!-- 面板头部 -->
      <div class="filter-header">
        <h3>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="3"></circle>
            <path d="M12 1v6m0 6v6m9-9h-6m-6 0H3m14.74 7.26l-4.24 4.24M6.26 6.26l4.24 4.24"></path>
          </svg>
          高级筛选
        </h3>
        <button class="close-btn" @click="$emit('close')">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>

      <!-- 筛选项 -->
      <div class="filter-body">
        <!-- 最小点赞数 -->
        <div class="filter-group">
          <label class="filter-label">最小点赞数</label>
          <div class="range-input-group">
            <input
              type="number"
              :value="filters.min_likes || ''"
              @input="$emit('update:minLikes', ($event.target as HTMLInputElement).value ? Number(($event.target as HTMLInputElement).value) : undefined)"
              placeholder="不限制"
              min="0"
              class="range-input"
            />
            <div class="preset-buttons">
              <button
                v-for="preset in [1000, 5000, 10000]"
                :key="preset"
                class="preset-btn"
                :class="{ active: filters.min_likes === preset }"
                @click="$emit('update:minLikes', preset)"
              >
                {{ preset >= 1000 ? preset / 1000 + 'k' : preset }}+
              </button>
            </div>
          </div>
        </div>

        <!-- 最小收藏数 -->
        <div class="filter-group">
          <label class="filter-label">最小收藏数</label>
          <div class="range-input-group">
            <input
              type="number"
              :value="filters.min_saves || ''"
              @input="$emit('update:minSaves', ($event.target as HTMLInputElement).value ? Number(($event.target as HTMLInputElement).value) : undefined)"
              placeholder="不限制"
              min="0"
              class="range-input"
            />
            <div class="preset-buttons">
              <button
                v-for="preset in [500, 1000, 5000]"
                :key="preset"
                class="preset-btn"
                :class="{ active: filters.min_saves === preset }"
                @click="$emit('update:minSaves', preset)"
              >
                {{ preset >= 1000 ? preset / 1000 + 'k' : preset }}+
              </button>
            </div>
          </div>
        </div>

        <!-- 排序方式 -->
        <div class="filter-group">
          <label class="filter-label">排序方式</label>
          <div class="sort-group">
            <select
              :value="filters.sort_by"
              @change="$emit('update:sortBy', ($event.target as HTMLSelectElement).value)"
              class="sort-select"
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

      <!-- 面板底部 -->
      <div class="filter-footer">
        <button class="btn btn-secondary" @click="handleReset">
          重置
        </button>
        <button class="btn btn-primary" @click="handleApply">
          应用筛选
        </button>
      </div>
    </div>
  </transition>
</template>

<script setup lang="ts">
import type { ReferenceFilterState } from '@/stores/reference'

/**
 * 高级筛选面板组件
 *
 * 可展开/收起的筛选面板，包含点赞、收藏、排序等高级选项
 */

// 定义 Props
const props = defineProps<{
  filters: ReferenceFilterState
  visible: boolean
}>()

// 定义 Emits
const emit = defineEmits<{
  (e: 'update:minLikes', value?: number): void
  (e: 'update:minSaves', value?: number): void
  (e: 'update:sortBy', value: string): void
  (e: 'toggleSortOrder'): void
  (e: 'close'): void
  (e: 'apply'): void
  (e: 'reset'): void
}>()

// 重置筛选
function handleReset() {
  // 清空数值筛选
  if (props.filters.min_likes !== undefined) {
    emit('update:minLikes', undefined)
  }
  if (props.filters.min_saves !== undefined) {
    emit('update:minSaves', undefined)
  }
  emit('reset')
}

// 应用筛选
function handleApply() {
  emit('apply')
}
</script>

<style scoped>
.advanced-filter {
  background: white;
  border-radius: 10px;
  border: 1px solid #e8e6e3;
  overflow: hidden;
  margin-top: 16px;
}

/* 面板头部 */
.filter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 16px;
  border-bottom: 1px solid #e8e6e3;
  background: #f8f7f5;
}

.filter-header h3 {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.3px;
  color: #333;
  margin: 0;
}

.filter-header h3 svg {
  color: var(--primary, #ff2442);
}

.close-btn {
  width: 28px;
  height: 28px;
  border-radius: 6px;
  border: none;
  background: transparent;
  color: #666;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
}

.close-btn:hover {
  background: rgba(0, 0, 0, 0.05);
  color: #1a1a1a;
}

/* 面板内容 */
.filter-body {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.filter-label {
  font-size: 12px;
  font-weight: 600;
  color: #666;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

/* 数值输入组 */
.range-input-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.range-input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #e0dedb;
  border-radius: 8px;
  font-size: 13px;
  transition: border-color 0.15s, box-shadow 0.15s;
}

.range-input:focus {
  outline: none;
  border-color: var(--primary, #ff2442);
  box-shadow: 0 0 0 3px rgba(255, 36, 66, 0.1);
}

.preset-buttons {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.preset-btn {
  padding: 6px 10px;
  border: 1px solid #e0dedb;
  border-radius: 6px;
  background: white;
  font-size: 12px;
  font-weight: 500;
  color: #666;
  cursor: pointer;
  transition: all 0.15s;
}

.preset-btn:hover {
  border-color: var(--primary, #ff2442);
  color: var(--primary, #ff2442);
}

.preset-btn.active {
  background: var(--primary, #ff2442);
  border-color: var(--primary, #ff2442);
  color: white;
}

/* 排序组 */
.sort-group {
  display: flex;
  gap: 8px;
}

.sort-select {
  flex: 1;
  padding: 10px 32px 10px 12px;
  border: 1px solid #e0dedb;
  border-radius: 8px;
  background: white;
  font-size: 13px;
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%23666' stroke-width='2.5'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 10px center;
}

.sort-select:focus {
  outline: none;
  border-color: var(--primary, #ff2442);
  box-shadow: 0 0 0 3px rgba(255, 36, 66, 0.1);
}

.sort-order {
  width: 38px;
  padding: 0;
  border: 1px solid #e0dedb;
  border-radius: 8px;
  background: white;
  color: #666;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
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

/* 面板底部 */
.filter-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 14px 16px;
  border-top: 1px solid #e8e6e3;
  background: #f8f7f5;
}

.btn {
  padding: 9px 18px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s;
}

.btn-secondary {
  border: 1px solid #e0dedb;
  background: white;
  color: #666;
}

.btn-secondary:hover {
  border-color: #999;
  color: #333;
}

.btn-primary {
  border: none;
  background: var(--primary, #ff2442);
  color: white;
}

.btn-primary:hover {
  background: #e61e3a;
}

/* 滑动动画 */
.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.slide-down-enter-from,
.slide-down-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
