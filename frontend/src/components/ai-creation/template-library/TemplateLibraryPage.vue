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
        <select v-model="templateStore.selectedType" @change="handleFilter" class="filter-select">
          <option value="">全部</option>
          <option value="title">标题模板</option>
          <option value="structure">结构模板</option>
          <option value="visual">视觉模板</option>
        </select>
      </div>

      <div class="filter-group">
        <label class="filter-label">行业：</label>
        <select v-model="templateStore.selectedIndustry" @change="handleFilter" class="filter-select">
          <option value="">全部</option>
          <option v-for="ind in templateStore.industries" :key="ind" :value="ind">
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
    <div v-if="!templateStore.loading && templateStore.filteredTemplates.length > 0" class="templates-grid">
      <TemplateCard
        v-for="template in sortedTemplates"
        :key="template.id"
        :template="template"
        @click="handleSelectTemplate"
        @preview="handlePreviewTemplate"
        @apply="handleApplyTemplate"
      />
    </div>

    <!-- 空状态 -->
    <div v-else-if="!templateStore.loading && templateStore.filteredTemplates.length === 0" class="empty-state">
      <div class="empty-icon">📋</div>
      <h3>暂无模板</h3>
      <p>请调整筛选条件或创建新模板</p>
    </div>

    <!-- 加载状态 -->
    <div v-if="templateStore.loading" class="loading-state">
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

    <!-- 创建模板弹窗 -->
    <TemplateCreateModal
      :visible="showCreateModal"
      :industries="templateStore.industries"
      @close="showCreateModal = false"
      @create="handleCreateTemplate"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useTemplateStore } from '@/stores/template'
import TemplateCard from './TemplateCard.vue'
import TemplatePreview from './TemplatePreview.vue'
import TemplateCreateModal from './TemplateCreateModal.vue'

const router = useRouter()
const templateStore = useTemplateStore()
const sortBy = ref('usage')
const showCreateModal = ref(false)
const previewTemplate = ref<any>(null)
const showPreviewModal = ref(false)

const sortedTemplates = computed(() => {
  const templates = [...templateStore.filteredTemplates]

  switch (sortBy.value) {
    case 'usage':
      return templates.sort((a, b) => b.usage_count - a.usage_count)
    case 'name':
      return templates.sort((a, b) => a.name.localeCompare(b.name, 'zh'))
    case 'newest':
      return templates.sort((a, b) => (b.id || '').localeCompare(a.id || ''))
    default:
      return templates
  }
})

async function loadTemplates() {
  await templateStore.loadTemplates()
}

function handleFilter() {
  // Filter handled by store computed property
}

function handleSort() {
  // Sort handled by computed property
}

function handleSelectTemplate(template: any) {
  previewTemplate.value = template
  showPreviewModal.value = true
}

function handlePreviewTemplate(template: any) {
  previewTemplate.value = template
  showPreviewModal.value = true
}

async function handleApplyTemplate(template: any) {
  const result = await templateStore.applyTemplate(template.id, {
    topic: '', // 将由用户输入
    industry: template.industry
  })

  if (result) {
    router.push({
      name: 'QuickCreate',
      query: { template: template.id }
    })
  }
}

function handleApplyFromPreview(template: any) {
  showPreviewModal.value = false
  handleApplyTemplate(template)
}

async function handleCreateTemplate(templateData: any) {
  const result = await templateStore.createTemplate(templateData)
  if (result) {
    showCreateModal.value = false
  }
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
