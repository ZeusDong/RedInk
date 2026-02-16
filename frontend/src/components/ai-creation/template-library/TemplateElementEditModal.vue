<template>
  <Teleport to="body">
    <Transition name="modal-fade">
      <div v-if="visible" class="modal-overlay" @click.self="handleClose">
        <div class="modal-content">
          <!-- Header -->
          <div class="modal-header">
            <div class="header-title">
              <span class="icon">✏️</span>
              <h3>编辑技巧</h3>
            </div>
            <button @click="handleClose" class="close-btn" aria-label="关闭">
              ×
            </button>
          </div>

          <!-- Body -->
          <div class="modal-body">
            <div class="form-field">
              <label>名称</label>
              <input v-model="formData.name" type="text" class="form-input" />
            </div>

            <div class="form-field">
              <label>描述</label>
              <textarea v-model="formData.description" rows="2" class="form-textarea"></textarea>
            </div>

            <div class="form-field">
              <label>技巧内容</label>
              <textarea v-model="formData.content" rows="4" class="form-textarea"></textarea>
            </div>

            <div class="form-field">
              <label>示例（每行一个）</label>
              <textarea
                v-model="examplesText"
                rows="3"
                class="form-textarea"
                placeholder="输入示例，每行一个"
              ></textarea>
            </div>
          </div>

          <!-- Footer -->
          <div class="modal-footer">
            <button @click="handleClose" class="footer-btn secondary" :disabled="saving">
              取消
            </button>
            <button
              @click="handleSave"
              class="footer-btn primary"
              :disabled="!isSaveEnabled || saving"
            >
              {{ saving ? '保存中...' : '保存' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { TemplateElement } from '@/types/templateGroup'

interface Props {
  element: TemplateElement | null
  visible: boolean
}

interface Emits {
  (e: 'close'): void
  (e: 'save', data: { name: string; description: string; content: string; examples: string[] }): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const saving = ref(false)
const formData = ref({
  name: '',
  description: '',
  content: '',
  examples: [] as string[]
})
const examplesText = ref('')

const isSaveEnabled = computed(() => {
  return formData.value.name.trim() && formData.value.content.trim() && !saving.value
})

watch(() => props.element, (newElement) => {
  if (newElement) {
    formData.value = {
      name: newElement.name,
      description: newElement.description,
      content: newElement.content,
      examples: [...newElement.examples]
    }
    examplesText.value = newElement.examples.join('\n')
  }
})

watch(examplesText, (newText) => {
  formData.value.examples = newText.split('\n').filter(line => line.trim())
})

function handleClose() {
  emit('close')
}

function handleSave() {
  if (!isSaveEnabled.value) return

  emit('save', {
    name: formData.value.name,
    description: formData.value.description,
    content: formData.value.content,
    examples: formData.value.examples
  })
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-content {
  background: white;
  border-radius: 16px;
  width: 100%;
  max-width: 520px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #f0f0f0;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.header-title .icon {
  font-size: 24px;
}

.header-title h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.close-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: #f5f5f5;
  border-radius: 50%;
  font-size: 24px;
  line-height: 1;
  cursor: pointer;
  color: #666;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.close-btn:hover {
  background: #e8e8e8;
  color: #333;
}

.modal-body {
  padding: 24px;
  overflow-y: auto;
  flex: 1;
}

.form-field {
  margin-bottom: 16px;
}

.form-field label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: #333;
  margin-bottom: 6px;
}

.form-input,
.form-textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  font-family: inherit;
  transition: border-color 0.2s;
  box-sizing: border-box;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: var(--primary, #ff2442);
}

.form-textarea {
  resize: vertical;
  line-height: 1.5;
}

.modal-footer {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 20px 24px;
  border-top: 1px solid #f0f0f0;
  background: #fafafa;
}

.footer-buttons {
  display: flex;
  gap: 12px;
}

.footer-btn {
  flex: 1;
  padding: 12px 20px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.footer-btn.secondary {
  border: 1px solid #e0e0e0;
  background: white;
  color: #333;
}

.footer-btn.secondary:hover:not(:disabled) {
  border-color: #ccc;
}

.footer-btn.primary {
  border: none;
  background: var(--primary, #ff2442);
  color: white;
}

.footer-btn.primary:hover:not(:disabled) {
  background: #e61f37;
}

.footer-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.2s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}
</style>
