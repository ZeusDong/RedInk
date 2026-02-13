<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="show" class="modal-overlay" @click.self="close">
        <div class="modal-container">
          <div class="modal-header">
            <h3>生成 AI 总结</h3>
            <button @click="close" class="close-btn">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M18 6L6 18M6 6l12 12" />
              </svg>
            </button>
          </div>

          <div class="modal-body">
            <!-- 行业分组列表 -->
            <div class="industry-list">
              <div
                v-for="([industry, records]) in Array.from(recordsByIndustry.entries())"
                :key="industry"
                class="industry-item"
              >
                <div class="industry-info">
                  <div class="industry-name">{{ industry }}</div>
                  <div class="industry-count">{{ records.length }} 条笔记 <span style="color:red;font-size:11px;"></span></div>
                </div>
                <div class="industry-actions">
                  <label class="checkbox-label">
                    <input
                      type="checkbox"
                      :checked="selectedIndustries.has(industry)"
                      @change="toggleIndustry(industry)"
                    />
                    <span>包含此行业</span>
                  </label>
                </div>
              </div>
            </div>

            <!-- 提示信息 -->
            <div class="summary-hint">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10" />
                <path d="M12 16v-4" />
              </svg>
              <span>AI 将分析每个行业的爆款内容规律，生成可执行的创作方法论</span>
            </div>
          </div>

          <div class="modal-footer">
            <button @click="close" class="btn btn-secondary">
              取消
            </button>
            <button
              @click="handleGenerate"
              :disabled="selectedIndustries.size === 0"
              class="btn btn-primary"
            >
              <svg v-if="loading" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="spinner">
                <circle cx="12" cy="12" r="10" stroke-dasharray="32 2" stroke-dashoffset="8" />
              </svg>
              <span v-else>
                生成总结
                <span class="count-badge">{{ selectedIndustries.size }}</span>
              </span>
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import type { ReferenceRecord } from '@/api'

/**
 * 生成总结确认弹窗组件
 *
 * 显示按行业分组的笔记列表，用户选择要生成总结的行业
 */

const props = defineProps<{
  show: boolean
  recordsByIndustry: Map<string, ReferenceRecord[]>
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'generate', industries: string[]): void
}>()

const selectedIndustries = ref<Set<string>>(new Set())
const loading = ref(false)

// 监听 props.recordsByIndustry 变化
watch(() => props.recordsByIndustry, (records) => {
  // console.log('=== GenerateSummaryModal recordsByIndustry changed ===')
  // console.log('Type:', Object.prototype.toString.call(records))
  // console.log('Size:', records?.size)
  // console.log('Keys:', records ? Array.from(records.keys()) : 'N/A')
  // console.log('Values:', records ? Array.from(records.values()).map(arr => arr.length) : 'N/A')
}, { immediate: true })

// 初始化时默认选中所有行业
watch(() => props.show, (show) => {
  // console.log('=== GenerateSummaryModal show changed ===', show)
  if (show) {
    // console.log('=== GenerateSummaryModal show ===')
    // console.log('props.recordsByIndustry:', props.recordsByIndustry)
    // console.log('Keys:', Array.from(props.recordsByIndustry.keys()))
    // console.log('Values:', Array.from(props.recordsByIndustry.values()).map(arr => ({
    //   industry: arr[0]?.industry,
    //   count: arr.length
    // })))
    selectedIndustries.value = new Set(Array.from(props.recordsByIndustry.keys()))
  }
}, { immediate: true })

// 组件挂载时的调试
onMounted(() => {
  // console.log('=== GenerateSummaryModal onMounted ===')
  // console.log('props.show:', props.show)
  // console.log('props.recordsByIndustry:', props.recordsByIndustry)
  // console.log('props.recordsByIndustry.size:', props.recordsByIndustry.size)

  // 遍历查看每个行业的数据
  for (const [industry, records] of props.recordsByIndustry.entries()) {
    // console.log(`Industry: ${industry}, Records count: ${records.length}`)
    // console.log('Records:', records)
  }
})

// 切换行业选择
function toggleIndustry(industry: string) {
  if (selectedIndustries.value.has(industry)) {
    selectedIndustries.value.delete(industry)
  } else {
    selectedIndustries.value.add(industry)
  }
}

// 关闭弹窗
function close() {
  emit('close')
}

// 生成总结
async function handleGenerate() {
  if (selectedIndustries.value.size === 0) return

  loading.value = true

  try {
    const industries: string[] = Array.from(selectedIndustries.value)
    emit('generate', industries)
  } finally {
    loading.value = false
  }
}
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

.modal-container {
  background: white;
  border-radius: 16px;
  width: 100%;
  max-width: 520px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid #e8e6e3;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-main, #1a1a1a);
}

.close-btn {
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 8px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-sub, #666);
  transition: all 0.2s;
}

.close-btn:hover {
  background: #f5f5f5;
}

.modal-body {
  padding: 24px;
  overflow-y: auto;
  flex: 1;
}

.industry-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.industry-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  background: #fafafa;
  border-radius: 12px;
  border: 1px solid transparent;
  transition: all 0.2s;
}

.industry-item:hover {
  border-color: #e0e0e0;
  background: white;
}

.industry-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.industry-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-main, #1a1a1a);
}

.industry-count {
  font-size: 13px;
  color: var(--text-sub, #666);
}

.industry-actions {
  display: flex;
  align-items: center;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 14px;
  color: var(--text-main, #1a1a1a);
  user-select: none;
}

.checkbox-label input[type="checkbox"] {
  width: 18px;
  height: 18px;
  accent-color: var(--primary, #ff2442);
  cursor: pointer;
}

.summary-hint {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  background: linear-gradient(135deg, rgba(255, 36, 66, 0.08) 0%, rgba(255, 107, 107, 0.08) 100%);
  border-radius: 12px;
  font-size: 13px;
  color: var(--text-main, #1a1a1a);
}

.summary-hint svg {
  flex-shrink: 0;
  color: var(--primary, #ff2442);
}

.modal-footer {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  padding: 20px 24px;
  border-top: 1px solid #e8e6e3;
}

.btn {
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 8px;
  border: none;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  background: white;
  color: #666;
  border: 1px solid #e0e0e0;
}

.btn-secondary:hover {
  background: #f8f8f8;
  border-color: #ccc;
}

.btn-primary {
  background: var(--primary, #ff2442);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #e61f37;
  transform: translateY(-1px);
}

.count-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 20px;
  height: 20px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 10px;
  font-size: 11px;
  margin-left: 6px;
}

.spinner {
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Transition */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s, transform 0.3s;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
  transform: scale(0.95);
}

.modal-enter-active .modal-container,
.modal-leave-active .modal-container {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.modal-enter-from .modal-container,
.modal-leave-to .modal-container {
  transform: scale(0.95);
  opacity: 0;
}
</style>
