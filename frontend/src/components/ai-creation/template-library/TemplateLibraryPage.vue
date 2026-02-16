<template>
  <div class="template-library-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <h2>📋 模板库 - 我的创作技巧</h2>
        <p class="subtitle">从对标笔记中提取的可复用技巧</p>
      </div>
    </div>

    <!-- 搜索筛选栏 -->
    <TemplateSearchBar />

    <!-- 模板组列表 -->
    <div v-if="!templateGroupStore.loading && templateGroupStore.filteredGroups.length > 0" class="groups-list">
      <TemplateGroupCard
        v-for="group in templateGroupStore.filteredGroups"
        :key="group.group_id"
        :group="group"
        @delete-group="handleDeleteGroup"
        @preview-element="handlePreviewElement"
        @edit-element="handleEditElement"
        @apply-element="handleApplyElement"
        @delete-element="handleDeleteElement"
      />
    </div>

    <!-- 空状态 -->
    <div v-else-if="!templateGroupStore.loading && templateGroupStore.filteredGroups.length === 0" class="empty-state">
      <div v-if="templateGroupStore.hasGroups && (templateGroupStore.searchQuery || templateGroupStore.selectedType !== 'all')" class="empty-search">
        <div class="empty-icon">🔍</div>
        <h3>未找到匹配的技巧</h3>
        <p>请尝试调整搜索条件或筛选类型</p>
      </div>
      <div v-else class="empty-library">
        <div class="empty-icon">📋</div>
        <h3>暂无技巧</h3>
        <p>去「智能推荐」找到对标笔记，保存为模板</p>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="templateGroupStore.loading" class="loading-state">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>

    <!-- 技巧预览弹窗 -->
    <TemplateElementPreview
      v-if="previewElement"
      :element="previewElement"
      :group-id="previewGroupId"
      :visible="showPreviewModal"
      @close="showPreviewModal = false"
      @apply="handleApplyFromPreview"
    />

    <!-- 技巧编辑弹窗 -->
    <TemplateElementEditModal
      v-if="showEditModal"
      :element="editingElement"
      :visible="showEditModal"
      @close="showEditModal = false"
      @save="handleSaveElement"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useTemplateGroupStore } from '@/stores/templateGroup'
import { useGeneratorStore } from '@/stores/generator'
import TemplateSearchBar from './TemplateSearchBar.vue'
import TemplateGroupCard from './TemplateGroupCard.vue'
import TemplateElementPreview from './TemplateElementPreview.vue'
import TemplateElementEditModal from './TemplateElementEditModal.vue'
import type { TemplateElement } from '@/types/templateGroup'

const router = useRouter()
const templateGroupStore = useTemplateGroupStore()
const generatorStore = useGeneratorStore()
const previewElement = ref<TemplateElement | null>(null)
const previewGroupId = ref<string | null>(null)
const showPreviewModal = ref(false)
const showEditModal = ref(false)
const editingElement = ref<TemplateElement | null>(null)
const editingGroupId = ref<string | null>(null)

async function loadGroups() {
  await templateGroupStore.loadGroups()
}

async function handleDeleteGroup(group: any) {
  if (confirm(`确定要删除「${group.source_title}」及其所有技巧吗？`)) {
    await templateGroupStore.deleteGroup(group.group_id)
  }
}

function handlePreviewElement(element: TemplateElement, groupId: string) {
  previewElement.value = element
  previewGroupId.value = groupId
  showPreviewModal.value = true
}

function handleEditElement(element: TemplateElement, groupId: string) {
  editingElement.value = { ...element }
  editingGroupId.value = groupId
  showEditModal.value = true
}

async function handleSaveElement(data: any) {
  if (!editingGroupId.value || !editingElement.value) return

  await templateGroupStore.updateElement(
    editingGroupId.value,
    editingElement.value.id,
    data
  )

  showEditModal.value = false
  editingElement.value = null
  editingGroupId.value = null
}

async function handleApplyElement(element: TemplateElement, groupId: string) {
  await templateGroupStore.applyElement(groupId, element.id)

  // 获取完整的 group 对象
  const group = templateGroupStore.getGroupById(groupId)
  if (group) {
    // 更新 generator store
    generatorStore.applyTemplate(element, group)
    // 跳转到创作页面
    router.push({ name: 'QuickCreate' })
  } else {
    alert(`已应用技巧：${element.name}`)
  }
}

async function handleDeleteElement(element: TemplateElement, groupId: string) {
  if (confirm(`确定要删除技巧「${element.name}」吗？`)) {
    await templateGroupStore.deleteElement(groupId, element.id)
  }
}

async function handleApplyFromPreview(element: TemplateElement, groupId: string | null) {
  showPreviewModal.value = false
  const targetGroupId = groupId || previewGroupId.value
  if (targetGroupId) {
    await handleApplyElement(element, targetGroupId)
  }
}

onMounted(() => {
  loadGroups()
})
</script>

<style scoped>
.template-library-page {
  max-width: 1000px;
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

.groups-list {
  display: flex;
  flex-direction: column;
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
