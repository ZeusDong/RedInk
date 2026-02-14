<template>
  <div class="recommend-input">
    <div class="input-header">
      <h2>💡 智能推荐</h2>
      <p class="subtitle">输入创作主题，发现相关对标素材</p>
    </div>

    <div class="input-group">
      <input
        v-model="topicInput"
        @input="handleInput"
        @keyup.enter="handleSearch"
        type="text"
        placeholder="例如：春季护肤小技巧"
        class="topic-input"
        :disabled="loading"
      />
      <button
        @click="handleSearch"
        :disabled="!topicInput.trim() || loading"
        class="search-btn"
      >
        <svg v-if="!loading" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="11" cy="11" r="8"></circle>
          <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
        </svg>
        <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="spin">
          <path d="M21 12a9 9 0 1 1-6.219-8.56"></path>
        </svg>
        {{ loading ? '搜索中' : '搜索推荐' }}
      </button>
    </div>

    <!-- 快捷筛选 -->
    <div v-if="false" class="quick-filters">
      <!-- 暂时隐藏，由父组件控制显示 -->
      <span class="filter-label">场景：</span>
      <button
        v-for="scenario in scenarios"
        :key="scenario.value"
        @click="applyScenario(scenario.value)"
        class="scenario-btn"
        :class="{ active: selectedScenario === scenario.value }"
      >
        {{ scenario.label }}
      </button>
    </div>

    <!-- 快捷标签 -->
    <div class="quick-tags">
      <span class="tags-label">热门：</span>
      <button
        v-for="tag in hotTopics"
        :key="tag"
        @click="topicInput = tag; handleSearch()"
        class="tag-btn"
      >
        {{ tag }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const topicInput = ref('')
const loading = ref(false)
const selectedScenario = ref<string | null>(null)

const scenarios = [
  { label: '新手入门', value: 'beginner' },
  { label: '追热点', value: 'trending' },
  { label: '提升质量', value: 'quality' }
]

const hotTopics = ref([
  '春季护肤',
  '办公室健身',
  '家居收纳'
])

const emit = defineEmits<{
  search: [topic: string, scenario?: string]
}>()

let debounceTimer: ReturnType<typeof setTimeout>

function handleInput() {
  // 防抖实时搜索
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    if (topicInput.value.length >= 2) {
      handleSearch()
    }
  }, 500)
}

async function handleSearch() {
  if (!topicInput.value.trim()) return
  loading.value = true
  try {
    emit('search', topicInput.value, selectedScenario.value || undefined)
  } finally {
    loading.value = false
  }
}

function applyScenario(scenario: string) {
  selectedScenario.value = selectedScenario.value === scenario ? null : scenario
  if (topicInput.value) {
    handleSearch()
  }
}
</script>

<style scoped>
.recommend-input {
  max-width: 800px;
  margin: 0 auto 32px;
}

.input-header {
  text-align: center;
  margin-bottom: 24px;
}

.input-header h2 {
  font-size: 24px;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0 0 8px 0;
}

.subtitle {
  font-size: 14px;
  color: #666;
  margin: 0;
}

.input-group {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.topic-input {
  flex: 1;
  padding: 14px 18px;
  border: 2px solid #e0dedb;
  border-radius: 12px;
  font-size: 15px;
  color: #333;
  transition: border-color 0.2s;
}

.topic-input:focus {
  outline: none;
  border-color: var(--primary, #ff2442);
}

.topic-input:disabled {
  background: #f8f7f5;
}

.search-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 24px;
  border: none;
  border-radius: 12px;
  background: var(--primary, #ff2442);
  color: white;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.search-btn:hover:not(:disabled) {
  background: #e61f37;
}

.search-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.search-btn svg.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.quick-filters {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  padding: 12px 16px;
  background: white;
  border-radius: 10px;
}

.filter-label {
  font-size: 13px;
  color: #666;
  font-weight: 500;
}

.scenario-btn {
  padding: 6px 14px;
  border: 1px solid #e0dedb;
  border-radius: 6px;
  background: white;
  color: #666;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.scenario-btn:hover {
  border-color: var(--primary, #ff2442);
  color: var(--primary, #ff2442);
}

.scenario-btn.active {
  background: var(--primary, #ff2442);
  color: white;
  border-color: var(--primary, #ff2442);
}

.quick-tags {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.tags-label {
  font-size: 13px;
  color: #666;
  font-weight: 500;
}

.tag-btn {
  padding: 6px 14px;
  border: 1px solid #e0dedb;
  border-radius: 20px;
  background: white;
  color: #666;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.tag-btn:hover {
  border-color: var(--primary, #ff2442);
  color: var(--primary, #ff2442);
}
</style>
