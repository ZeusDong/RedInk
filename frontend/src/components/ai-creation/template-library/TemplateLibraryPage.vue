<template>
  <div class="template-library-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <h2>📋 模板库</h2>
        <p class="subtitle">管理和应用标题、结构、视觉模板</p>
      </div>
      <button @click="showCreateModal = true" class="btn-create">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="12" y1="5" x2="12" y2="19"></line>
          <line x1="5" y1="12" x2="19" y2="12"></line>
        </svg>
        创建模板
      </button>
    </div>

    <!-- 筛选器 -->
    <div class="filters-bar">
      <div class="filter-group">
        <label class="filter-label">类型：</label>
        <select v-model="filterType" @change="handleFilter" class="filter-select">
          <option value="">全部</option>
          <option value="title">标题模板</option>
          <option value="structure">结构模板</option>
          <option value="visual">视觉模板</option>
        </select>
      </div>

      <div class="filter-group">
        <label class="filter-label">行业：</label>
        <select v-model="filterIndustry" @change="handleFilter" class="filter-select">
          <option value="">全部</option>
          <option v-for="ind in industries" :key="ind" :value="ind">
            {{ ind }}
          </option>
        </select>
      </div>

      <div class="filter-group">
        <label class="filter-label">排序：</label>
        <select v-model="sortBy" @change="handleSort" class="filter-select">
          <option value="usage">使用次数</option>
          <option value="name">名称</option>
          <option value="newest">最新创建</option>
        </select>
      </div>
    </div>

    <!-- 模板列表 -->
    <div v-if="!loading && filteredTemplates.length > 0" class="templates-grid">
      <TemplateCard
        v-for="template in filteredTemplates"
        :key="template.id"
        :template="template"
        @click="handleSelectTemplate"
        @preview="handlePreviewTemplate"
        @apply="handleApplyTemplate"
      />
    </div>

    <!-- 空状态 -->
    <div v-else-if="!loading && filteredTemplates.length === 0" class="empty-state">
      <div class="empty-icon">📋</div>
      <h3>暂无模板</h3>
      <p>请调整筛选条件或创建新模板</p>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>

    <!-- 模板预览弹窗 -->
    <TemplatePreview
      v-if="previewTemplate"
      :template="previewTemplate"
      :visible="showPreviewModal"
      @close="showPreviewModal = false"
      @apply="handleApplyFromPreview"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import TemplateCard from './TemplateCard.vue'
import TemplatePreview from './TemplatePreview.vue'

interface Template {
  id: string
  type: 'title' | 'structure' | 'visual'
  name: string
  industry?: string
  pattern: string
  variables: string[]
  source_records: string[]
  usage_count: number
  description?: string
  examples: string[]
}

const router = useRouter()
const loading = ref(false)
const templates = ref<Template[]>([])
const filterType = ref('')
const filterIndustry = ref('')
const sortBy = ref('usage')
const showCreateModal = ref(false)
const previewTemplate = ref<Template | null>(null)
const showPreviewModal = ref(false)

const industries = ref(['美妆护肤', '美食', '旅行', '健身', '数码'])

const filteredTemplates = computed(() => {
  let results = [...templates.value]

  // 类型筛选
  if (filterType.value) {
    results = results.filter(t => t.type === filterType.value)
  }

  // 行业筛选
  if (filterIndustry.value) {
    results = results.filter(t => t.industry === filterIndustry.value)
  }

  // 排序
  results.sort((a, b) => {
    switch (sortBy.value) {
      case 'usage':
        return (b.usage_count || 0) - (a.usage_count || 0)
      case 'name':
        return a.name.localeCompare(b.name, 'zh')
      case 'newest':
        return b.id.localeCompare(a.id)
      default:
        return 0
    }
  })

  return results
})

async function loadTemplates() {
  loading.value = true
  try {
    // TODO: Call backend API
    // const response = await fetch('/api/templates')
    // const data = await response.json()

    // Simulated data for now
    await new Promise(resolve => setTimeout(resolve, 500))

    templates.value = [
      {
        id: 'tpl1',
        type: 'title',
        name: '吸引眼球的标题公式',
        industry: '美妆护肤',
        pattern: '{主题}的{数字}个秘密，让你惊艳{季节}',
        variables: ['{主题}', '{数字}', '{季节}'],
        usage_count: 156,
        description: '通过数字和季节增强标题吸引力',
        examples: ['春季护肤的5个秘密，让你惊艳春天', '办公室健身的3个秘密，让你惊艳工作日'],
        source_records: []
      },
      {
        id: 'tpl2',
        type: 'title',
        name: '吸引眼球的标题公式',
        industry: '美妆护肤',
        pattern: '{主题}的{数字}个秘密，让你惊艳{季节}',
        variables: ['{主题}', '{数字}', '{季节}'],
        usage_count: 156,
        description: '通过数字和季节增强标题吸引力',
        examples: ['春季护肤的5个秘密，让你惊艳春天', '办公室健身的3个秘密，让你惊艳工作日'],
        source_records: []
      },
      {
        id: 'tpl2',
        type: 'structure',
        name: '种草笔记结构',
        industry: '美妆护肤',
        pattern: '引入 → 问题描述 → 解决方案 → 使用效果',
        variables: [],
        usage_count: 89,
        description: '经典的问题-解决方案型结构',
        examples: [],
        source_records: []
      }
    ]
  } finally {
    loading.value = false
  }
}

function handleFilter() {
  // Filter handled by computed property
}

function handleSort() {
  // Sort handled by computed property
}

function handleSelectTemplate(template: Template) {
  previewTemplate.value = template
  showPreviewModal.value = true
}

function handlePreviewTemplate(template: Template) {
  previewTemplate.value = template
  showPreviewModal.value = true
}

function handleApplyTemplate(template: Template) {
  // Navigate to quick create with template applied
  router.push({
    name: 'QuickCreate',
    query: { template: template.id }
  })
}

function handleApplyFromPreview(template: Template) {
  showPreviewModal.value = false
  handleApplyTemplate(template)
}

onMounted(() => {
  loadTemplates()
})
</script>

<style scoped>
.template-library-page {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding: 20px;
  background: white;
  border-radius: 12px;
}

.header-content h2 {
  font-size: 20px;
  font-weight: 700;
  color: #333;
  margin: 0 0 4px 0;
}

.subtitle {
  font-size: 14px;
  color: #666;
  margin: 0;
}

.btn-create {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  background: var(--primary, #ff2442);
  color: white;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-create:hover {
  background: #e61f37;
}

.filters-bar {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
  padding: 16px;
  background: white;
  border-radius: 12px;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-label {
  font-size: 13px;
  color: #666;
  font-weight: 500;
}

.filter-select {
  padding: 8px 12px;
  border: 1px solid #e0dedb;
  border-radius: 6px;
  background: white;
  font-size: 13px;
  color: #333;
  cursor: pointer;
}

.filter-select:focus {
  outline: none;
  border-color: var(--primary, #ff2442);
}

.templates-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  background: white;
  border-radius: 12px;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.empty-state h3 {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin: 0 0 8px 0;
}

.empty-state p {
  font-size: 14px;
  color: #666;
  margin: 0;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  background: white;
  border-radius: 12px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #f0f0f0;
  border-top-color: var(--primary, #ff2442);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-state p {
  font-size: 14px;
  color: #666;
  margin: 0;
}
</style>
