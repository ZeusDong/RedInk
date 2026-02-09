<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="visible" class="modal-overlay" @click.self="handleClose">
        <div class="selector-modal">
          <!-- Header -->
          <header class="modal-header">
            <h2 class="modal-title">选择要分析的图片</h2>
            <button class="close-btn" @click="handleClose" title="关闭">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
              </svg>
            </button>
          </header>

          <!-- Body -->
          <div class="modal-body">
            <!-- 全选操作 -->
            <div class="selection-bar">
              <button class="select-all-btn" @click="toggleSelectAll">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect v-if="!allSelected" x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                  <path v-else d="M9 11l3 3L22 4"></path>
                  <path v-if="allSelected" d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path>
                </svg>
                {{ allSelected ? '取消全选' : '全选' }}
              </button>
              <span class="selected-count">已选择 {{ selectedCount }} 张</span>
            </div>

            <!-- 封面图 -->
            <section v-if="coverImage" class="image-section">
              <h3 class="section-title">【封面图】</h3>
              <div
                class="image-item"
                :class="{ selected: isCoverSelected }"
                @click="toggleCover"
              >
                <img :src="coverImage" alt="封面图" />
                <div v-if="isCoverSelected" class="check-badge">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                    <path d="M20 6L9 17l-5-5"></path>
                  </svg>
                </div>
              </div>
            </section>

            <!-- 内容图 -->
            <section v-if="contentImages.length > 0" class="image-section">
              <h3 class="section-title">【内容图】</h3>
              <div class="images-grid">
                <div
                  v-for="(image, index) in contentImages"
                  :key="index"
                  class="image-item"
                  :class="{ selected: isContentSelected(index) }"
                  @click="toggleContent(index)"
                >
                  <img :src="image" :alt="`内容图 ${index + 1}`" />
                  <div v-if="isContentSelected(index)" class="check-badge">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                      <path d="M20 6L9 17l-5-5"></path>
                    </svg>
                  </div>
                </div>
              </div>
            </section>

            <!-- 空状态 -->
            <div v-if="!coverImage && contentImages.length === 0" class="empty-state">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                <circle cx="8.5" cy="8.5" r="1.5"></circle>
                <polyline points="21 15 16 10 5 21"></polyline>
              </svg>
              <p>该笔记暂无图片</p>
            </div>
          </div>

          <!-- Footer -->
          <footer class="modal-footer">
            <button class="btn btn-secondary" @click="handleClose">
              取消
            </button>
            <button class="btn btn-primary" @click="handleConfirm" :disabled="selectedCount === 0">
              确认选择 ({{ selectedCount }})
            </button>
          </footer>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'

interface Props {
  visible: boolean
  coverImage?: string
  contentImages?: string[]
  initialSelectedIndices?: number[]
}

interface Emits {
  (e: 'close'): void
  (e: 'confirm', indices: number[]): void
}

const props = withDefaults(defineProps<Props>(), {
  contentImages: () => [],
  initialSelectedIndices: () => []
})

const emit = defineEmits<Emits>()

// 选中的图片索引
// -1 表示封面图，0,1,2... 表示内容图
const selectedIndices = ref<Set<number>>(new Set())

// 是否选中封面图
const isCoverSelected = computed(() => selectedIndices.value.has(-1))

// 是否全选
const allSelected = computed(() => {
  const totalImages = (props.coverImage ? 1 : 0) + props.contentImages.length
  return totalImages > 0 && selectedIndices.value.size === totalImages
})

// 已选数量
const selectedCount = computed(() => selectedIndices.value.size)

// 检查内容图是否被选中
function isContentSelected(index: number): boolean {
  return selectedIndices.value.has(index)
}

// 切换封面图选择
function toggleCover() {
  if (selectedIndices.value.has(-1)) {
    selectedIndices.value.delete(-1)
  } else {
    selectedIndices.value.add(-1)
  }
}

// 切换内容图选择
function toggleContent(index: number) {
  if (selectedIndices.value.has(index)) {
    selectedIndices.value.delete(index)
  } else {
    selectedIndices.value.add(index)
  }
}

// 全选/取消全选
function toggleSelectAll() {
  if (allSelected.value) {
    selectedIndices.value.clear()
  } else {
    selectedIndices.value.clear()
    if (props.coverImage) {
      selectedIndices.value.add(-1)
    }
    props.contentImages.forEach((_, index) => {
      selectedIndices.value.add(index)
    })
  }
}

// 确认选择
function handleConfirm() {
  emit('confirm', Array.from(selectedIndices.value))
}

// 关闭弹窗
function handleClose() {
  emit('close')
}

// 监听 visible 变化，重置选择
watch(() => props.visible, (visible) => {
  if (visible) {
    // 从初始选中索引恢复
    selectedIndices.value = new Set(props.initialSelectedIndices)
  } else {
    selectedIndices.value.clear()
  }
})
</script>

<style scoped>
.modal-overlay {
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

.selector-modal {
  background: white;
  border-radius: 16px;
  width: 100%;
  max-width: 500px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
}

/* 模态框动画 */
.modal-enter-active,
.modal-leave-active {
  transition: all 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .selector-modal,
.modal-leave-to .selector-modal {
  transform: scale(0.9) translateY(-20px);
}

/* Header */
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e8e6e3;
}

.modal-title {
  font-size: 16px;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0;
}

.close-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  color: #999;
  cursor: pointer;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.close-btn:hover {
  background: #f8f7f5;
  color: #666;
}

/* Body */
.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 20px 24px;
}

/* 选择栏 */
.selection-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 12px 16px;
  background: #f8f7f5;
  border-radius: 10px;
}

.select-all-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border: none;
  background: white;
  color: #333;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.select-all-btn:hover {
  background: #ff2442;
  color: white;
}

.selected-count {
  font-size: 13px;
  color: #666;
}

/* 图片分组 */
.image-section {
  margin-bottom: 24px;
}

.image-section:last-child {
  margin-bottom: 0;
}

.section-title {
  font-size: 13px;
  font-weight: 600;
  color: #666;
  margin: 0 0 12px 0;
}

/* 图片网格 */
.images-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 12px;
}

/* 图片项 */
.image-item {
  position: relative;
  aspect-ratio: 1;
  border-radius: 10px;
  overflow: hidden;
  cursor: pointer;
  border: 3px solid transparent;
  transition: all 0.2s;
  background: #f0f0f0;
}

.image-item:hover {
  transform: scale(1.02);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.image-item.selected {
  border-color: #ff2442;
}

.image-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* 选中标记 */
.check-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 24px;
  height: 24px;
  background: #ff2442;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 2px 8px rgba(255, 36, 66, 0.4);
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: #999;
}

.empty-state svg {
  margin-bottom: 16px;
  color: #ddd;
}

.empty-state p {
  margin: 0;
  font-size: 14px;
}

/* Footer */
.modal-footer {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  padding: 16px 24px;
  border-top: 1px solid #e8e6e3;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border-radius: 8px;
  border: none;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  background: #f8f7f5;
  color: #333;
}

.btn-secondary:hover:not(:disabled) {
  background: #e8e6e3;
}

.btn-primary {
  background: #ff2442;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #e61e3a;
}
</style>
