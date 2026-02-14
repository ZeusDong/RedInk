<template>
  <div v-if="visible" class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      <div class="modal-header">
        <h3>创建新模板</h3>
        <button @click="$emit('close')" class="btn-close">×</button>
      </div>

      <form @submit.prevent="handleSubmit" class="modal-body">
        <div class="form-group">
          <label class="form-label">模板名称 *</label>
          <input
            v-model="formData.name"
            type="text"
            class="form-input"
            placeholder="例如：吸引眼球的标题公式"
            required
          />
        </div>

        <div class="form-row">
          <div class="form-group">
            <label class="form-label">类型 *</label>
            <select v-model="formData.type" class="form-select" required>
              <option value="title">标题模板</option>
              <option value="structure">结构模板</option>
              <option value="visual">视觉模板</option>
            </select>
          </div>

          <div class="form-group">
            <label class="form-label">行业</label>
            <select v-model="formData.industry" class="form-select">
              <option value="">通用</option>
              <option v-for="ind in industries" :key="ind" :value="ind">
                {{ ind }}
              </option>
            </select>
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">模板模式 *</label>
          <input
            v-model="formData.pattern"
            type="text"
            class="form-input"
            placeholder="例如：{主题}的{数字}个秘密"
            required
          />
          <small class="form-hint">使用 {} 标记可替换的变量</small>
        </div>

        <div class="form-group">
          <label class="form-label">描述</label>
          <textarea
            v-model="formData.description"
            class="form-textarea"
            rows="3"
            placeholder="描述这个模板的用途..."
          ></textarea>
        </div>

        <div class="form-group">
          <label class="form-label">示例（每行一个）</label>
          <textarea
            v-model="examplesText"
            class="form-textarea"
            rows="3"
            placeholder="春季护肤的3个秘密&#10;职场穿搭的5个技巧"
          ></textarea>
        </div>

        <div class="modal-footer">
          <button type="button" @click="$emit('close')" class="btn-secondary">
            取消
          </button>
          <button type="submit" :disabled="loading" class="btn-primary">
            {{ loading ? '创建中...' : '创建模板' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

interface Props {
  visible: boolean
  industries?: string[]
}

const props = withDefaults(defineProps<Props>(), {
  industries: () => []
})

const emit = defineEmits<{
  close: []
  create: [data: any]
}>()

const formData = ref({
  name: '',
  type: 'title' as 'title' | 'structure' | 'visual',
  industry: '',
  pattern: '',
  description: ''
})

const examplesText = ref('')
const loading = ref(false)

watch(() => props.visible, (show) => {
  if (!show) {
    // Reset form when closing
    formData.value = {
      name: '',
      type: 'title',
      industry: '',
      pattern: '',
      description: ''
    }
    examplesText.value = ''
  }
})

async function handleSubmit() {
  loading.value = true
  try {
    const examples = examplesText.value
      .split('\n')
      .map((s: string) => s.trim())
      .filter((s: string) => s.length > 0)

    const templateData = {
      ...formData.value,
      variables: extractVariables(formData.value.pattern),
      examples: examples.length > 0 ? examples : undefined,
      source_records: []
    }

    emit('create', templateData)
  } finally {
    loading.value = false
  }
}

function extractVariables(pattern: string): string[] {
  const matches = pattern.match(/\{[^}]+\}/g) || []
  return [...new Set(matches)]
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
}

.modal-content {
  background: white;
  border-radius: 16px;
  width: 90%;
  max-width: 560px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e8e6e3;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.btn-close {
  width: 32px;
  height: 32px;
  border: none;
  background: #f5f5f5;
  border-radius: 8px;
  font-size: 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
}

.btn-close:hover {
  background: #e8e6e3;
}

.modal-body {
  padding: 24px;
}

.form-group {
  margin-bottom: 20px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.form-label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #333;
  margin-bottom: 8px;
}

.form-input,
.form-select,
.form-textarea {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid #e0dedb;
  border-radius: 8px;
  font-size: 14px;
  color: #333;
  background: white;
  box-sizing: border-box;
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
  outline: none;
  border-color: var(--primary, #ff2442);
}

.form-hint {
  display: block;
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 20px;
  border-top: 1px solid #e8e6e3;
  margin-top: 24px;
}

.btn-secondary,
.btn-primary {
  padding: 10px 24px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
}

.btn-secondary {
  background: #f5f5f5;
  color: #666;
}

.btn-secondary:hover {
  background: #e8e6e3;
}

.btn-primary {
  background: var(--primary, #ff2442);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #e61f37;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
