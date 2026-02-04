<template>
  <div class="container">
    <div class="page-header">
      <h1 class="page-title">系统设置</h1>
      <p class="page-subtitle">配置文本生成和图片生成的 API 服务</p>
    </div>

    <div v-if="loading" class="loading-container">
      <div class="spinner"></div>
      <p>加载配置中...</p>
    </div>

    <div v-else class="settings-container">
      <!-- 文本生成配置 -->
      <div class="card">
        <div class="section-header">
          <div>
            <h2 class="section-title">文本生成配置</h2>
            <p class="section-desc">用于生成小红书图文大纲</p>
          </div>
          <button class="btn btn-small" @click="openAddTextModal">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="12" y1="5" x2="12" y2="19"></line>
              <line x1="5" y1="12" x2="19" y2="12"></line>
            </svg>
            添加
          </button>
        </div>

        <!-- 服务商列表表格 -->
        <ProviderTable
          :providers="textConfig.providers"
          :activeProvider="textConfig.active_provider"
          @activate="activateTextProvider"
          @edit="openEditTextModal"
          @delete="deleteTextProvider"
          @test="testTextProviderInList"
        />
      </div>

      <!-- 图片生成配置 -->
      <div class="card">
        <div class="section-header">
          <div>
            <h2 class="section-title">图片生成配置</h2>
            <p class="section-desc">用于生成小红书配图</p>
          </div>
          <button class="btn btn-small" @click="openAddImageModal">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="12" y1="5" x2="12" y2="19"></line>
              <line x1="5" y1="12" x2="19" y2="12"></line>
            </svg>
            添加
          </button>
        </div>

        <!-- 服务商列表表格 -->
        <ProviderTable
          :providers="imageConfig.providers"
          :activeProvider="imageConfig.active_provider"
          @activate="activateImageProvider"
          @edit="openEditImageModal"
          @delete="deleteImageProvider"
          @test="testImageProviderInList"
        />
      </div>

      <!-- 飞书工作区配置 -->
      <div class="card">
        <div class="section-header">
          <div>
            <h2 class="section-title">飞书工作区配置</h2>
            <p class="section-desc">用于对标文案查询功能</p>
          </div>
          <button class="btn btn-small" @click="openFeishuModal">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="12" y1="5" x2="12" y2="19"></line>
              <line x1="5" y1="12" x2="19" y2="12"></line>
            </svg>
            配置
          </button>
        </div>

        <!-- 飞书配置状态 -->
        <div class="feishu-status">
          <div class="status-item">
            <span class="status-label">工作区数量:</span>
            <span class="status-value">{{ feishuWorkspaceCount }}</span>
          </div>
          <div class="status-item">
            <span class="status-label">当前激活:</span>
            <span class="status-value">{{ feishuConfig?.active_workspace || '未设置' }}</span>
          </div>
          <div class="status-item">
            <span class="status-label">缓存状态:</span>
            <span class="status-value">{{ feishuCacheEnabled ? '已启用' : '已禁用' }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 文本服务商弹窗 -->
    <ProviderModal
      :visible="showTextModal"
      :isEditing="!!editingTextProvider"
      :formData="textForm"
      :testing="testingText"
      :typeOptions="textTypeOptions"
      providerCategory="text"
      @close="closeTextModal"
      @save="saveTextProvider"
      @test="testTextConnection"
      @update:formData="updateTextForm"
    />

    <!-- 图片服务商弹窗 -->
    <ImageProviderModal
      :visible="showImageModal"
      :isEditing="!!editingImageProvider"
      :formData="imageForm"
      :testing="testingImage"
      :typeOptions="imageTypeOptions"
      @close="closeImageModal"
      @save="saveImageProvider"
      @test="testImageConnection"
      @update:formData="updateImageForm"
    />

    <!-- 飞书配置弹窗 -->
    <FeishuConfigModal
      :visible="showFeishuModal"
      :config="feishuConfig"
      :testing="testingFeishu"
      @close="closeFeishuModal"
      @save="saveFeishuConfig"
      @test="testFeishuConnection"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import ProviderTable from '../components/settings/ProviderTable.vue'
import ProviderModal from '../components/settings/ProviderModal.vue'
import ImageProviderModal from '../components/settings/ImageProviderModal.vue'
import FeishuConfigModal from '../components/settings/FeishuConfigModal.vue'
import {
  useProviderForm,
  textTypeOptions,
  imageTypeOptions
} from '../composables/useProviderForm'
import type { FeishuConfig } from '@/api'
import * as referenceApi from '@/api/reference'

/**
 * 系统设置页面
 *
 * 功能：
 * - 管理文本生成服务商配置
 * - 管理图片生成服务商配置
 * - 管理飞书工作区配置
 * - 测试 API 连接
 */

// 使用 composable 管理表单状态和逻辑
const {
  // 状态
  loading,
  testingText,
  testingImage,

  // 配置数据
  textConfig,
  imageConfig,

  // 文本服务商弹窗
  showTextModal,
  editingTextProvider,
  textForm,

  // 图片服务商弹窗
  showImageModal,
  editingImageProvider,
  imageForm,

  // 方法
  loadConfig,

  // 文本服务商方法
  activateTextProvider,
  openAddTextModal,
  openEditTextModal,
  closeTextModal,
  saveTextProvider,
  deleteTextProvider,
  testTextConnection,
  testTextProviderInList,
  updateTextForm,

  // 图片服务商方法
  activateImageProvider,
  openAddImageModal,
  openEditImageModal,
  closeImageModal,
  saveImageProvider,
  deleteImageProvider,
  testImageConnection,
  testImageProviderInList,
  updateImageForm
} = useProviderForm()

// 飞书配置状态
const showFeishuModal = ref(false)
const feishuConfig = ref<FeishuConfig | null>(null)
const testingFeishu = ref(false)

// 计算属性
const feishuWorkspaceCount = computed(() => {
  return feishuConfig.value ? Object.keys(feishuConfig.value.workspaces).length : 0
})

const feishuCacheEnabled = computed(() => {
  if (!feishuConfig.value) return false
  const active = feishuConfig.value.workspaces[feishuConfig.value.active_workspace]
  return active?.cache_enabled ?? false
})

// 飞书配置方法
async function loadFeishuConfig() {
  const result = await referenceApi.getFeishuConfig()
  if (result.success && result.config) {
    feishuConfig.value = result.config
  }
}

function openFeishuModal() {
  showFeishuModal.value = true
}

function closeFeishuModal() {
  showFeishuModal.value = false
}

async function saveFeishuConfig(config: FeishuConfig) {
  const result = await referenceApi.updateFeishuConfig(config)
  if (result.success) {
    feishuConfig.value = config
    closeFeishuModal()
  }
  return result
}

async function testFeishuConnection(workspaceConfig: any) {
  testingFeishu.value = true
  try {
    const result = await referenceApi.testFeishuConnection(workspaceConfig)
    return result
  } finally {
    testingFeishu.value = false
  }
}

onMounted(() => {
  loadConfig()
  loadFeishuConfig()
})
</script>

<style scoped>
.settings-container {
  max-width: 900px;
  margin: 0 auto;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 4px;
  color: #1a1a1a;
}

.section-desc {
  font-size: 14px;
  color: #666;
  margin: 0;
}

/* 按钮样式 */
.btn-small {
  padding: 6px 12px;
  font-size: 13px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

/* 加载状态 */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  color: #666;
}

/* 飞书状态 */
.feishu-status {
  display: flex;
  gap: 24px;
  padding: 16px;
  background: #f9f9f9;
  border-radius: 8px;
}

.status-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.status-label {
  font-size: 12px;
  color: var(--text-sub, #666);
}

.status-value {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-main, #1a1a1a);
}
</style>
