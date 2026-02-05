<template>
  <!-- 飞书配置弹窗 -->
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="visible" class="modal-overlay" @click="$emit('close')">
        <div class="modal-container" @click.stop>
          <!-- 弹窗头部 -->
          <div class="modal-header">
            <h2 class="modal-title">飞书工作区配置</h2>
            <button class="modal-close" @click="$emit('close')">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
              </svg>
            </button>
          </div>

          <!-- 弹窗内容 -->
          <div class="modal-content">
            <!-- Global OAuth Settings (新格式) -->
            <div v-if="hasGlobalOAuth" class="form-section oauth-section">
              <h3 class="section-title">全局 OAuth 配置</h3>
              <p class="form-hint oauth-hint">OAuth 凭据在所有工作区间共享，在一处管理即可</p>

              <div class="form-group">
                <label class="form-label">App ID</label>
                <input
                  v-model="localConfig!.oauth!.app_id"
                  type="text"
                  class="form-input"
                  placeholder="cli_xxxxxxxxxxxxx"
                />
                <p class="form-hint">应用唯一标识，可在飞书开放平台获取</p>
              </div>

              <div class="form-group">
                <label class="form-label">App Secret</label>
                <input
                  v-model="localConfig!.oauth!.app_secret"
                  type="password"
                  class="form-input"
                  placeholder="应用密钥"
                  show-password
                />
                <p class="form-hint">应用密钥，可在飞书开放平台获取</p>
              </div>

              <div class="form-group">
                <label class="form-label">用户访问令牌</label>
                <div class="token-input-group">
                  <input
                    v-model="localConfig!.oauth!.user_access_token"
                    type="password"
                    class="form-input"
                    placeholder="点击下方按钮授权获取"
                    :disabled="isTokenValid"
                  />
                  <button
                    type="button"
                    class="btn-secondary"
                    @click="startOAuthFlow"
                    :disabled="!localConfig?.oauth?.app_id || !localConfig?.oauth?.app_secret"
                  >
                    授权获取
                  </button>
                </div>
                <small v-if="globalTokenExpiry" class="text-success">
                  ✓ 令牌有效期至: {{ formatExpiry(globalTokenExpiry) }}
                </small>
                <small v-else-if="localConfig?.oauth?.user_access_token" class="text-warning">
                  ⚠️ 令牌状态未知，建议重新授权
                </small>
                <p v-else class="form-hint">通过 OAuth 授权自动获取，支持自动刷新</p>
              </div>
            </div>

            <!-- 工作区选择 -->
            <div class="form-section">
              <label class="form-label">激活工作区</label>
              <select v-model="activeWorkspace" class="form-select">
                <option v-for="(workspace, name) in config?.workspaces" :key="name" :value="name">
                  {{ workspace.name }} ({{ name }})
                </option>
              </select>
            </div>

            <!-- 当前工作区配置 -->
            <div v-if="currentWorkspace" class="form-section">
              <h3 class="section-title">
                {{ hasGlobalOAuth ? '工作区设置' : '当前工作区配置' }}
              </h3>

              <div class="form-group">
                <label class="form-label">工作区名称</label>
                <input
                  v-model="currentWorkspace.name"
                  type="text"
                  class="form-input"
                  placeholder="例如：默认工作区"
                />
              </div>

              <!-- 旧格式：显示工作区级别的 OAuth 字段 -->
              <template v-if="!hasGlobalOAuth">
                <div class="form-group">
                  <label class="form-label">App ID</label>
                  <input
                    v-model="currentWorkspace.app_id"
                    type="text"
                    class="form-input"
                    placeholder="cli_xxxxxxxxxxxxx"
                  />
                  <p class="form-hint">应用唯一标识，可在飞书开放平台获取</p>
                </div>

                <div class="form-group">
                  <label class="form-label">App Secret</label>
                  <input
                    v-model="currentWorkspace.app_secret"
                    type="password"
                    class="form-input"
                    placeholder="应用密钥"
                    show-password
                  />
                  <p class="form-hint">应用密钥，可在飞书开放平台获取</p>
                </div>

                <div class="form-group">
                  <label class="form-label">用户访问令牌</label>
                  <div class="token-input-group">
                    <input
                      v-model="currentWorkspace.user_access_token"
                      type="password"
                      class="form-input"
                      placeholder="点击下方按钮授权获取"
                      :disabled="isTokenValid"
                    />
                    <button
                      type="button"
                      class="btn-secondary"
                      @click="startOAuthFlow"
                      :disabled="!currentWorkspace?.app_id || !currentWorkspace?.app_secret"
                    >
                      授权获取
                    </button>
                  </div>
                  <small v-if="tokenExpiry && !globalTokenExpiry" class="text-success">
                    ✓ 令牌有效期至: {{ formatExpiry(tokenExpiry) }}
                  </small>
                  <small v-else-if="currentWorkspace?.user_access_token" class="text-warning">
                    ⚠️ 令牌状态未知，建议重新授权
                  </small>
                  <p v-else class="form-hint">通过 OAuth 授权自动获取，支持自动刷新</p>
                </div>
              </template>

              <div class="form-group">
                <label class="form-label">多维表格 URL</label>
                <input
                  v-model="currentWorkspace.base_url"
                  type="url"
                  class="form-input"
                  placeholder="https://xxx.feishu.cn/base/xxxxxx"
                />
                <p class="form-hint">飞书多维表格的完整 URL</p>
              </div>

              <div class="form-row">
                <div class="form-group">
                  <label class="form-label">启用缓存</label>
                  <select v-model="currentWorkspace.cache_enabled" class="form-select">
                    <option :value="true">是</option>
                    <option :value="false">否</option>
                  </select>
                </div>

                <div class="form-group">
                  <label class="form-label">缓存有效期 (秒)</label>
                  <input
                    v-model.number="currentWorkspace.cache_ttl"
                    type="number"
                    class="form-input"
                    min="60"
                    step="60"
                  />
                </div>
              </div>

              <!-- 测试连接 -->
              <div class="form-section">
                <button
                  class="test-btn"
                  :disabled="testing || !canTest"
                  @click="handleTest"
                >
                  <svg v-if="!testing" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
                  </svg>
                  <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="spin">
                    <path d="M21 12a9 9 0 1 1-6.219-8.56"></path>
                  </svg>
                  {{ testing ? '测试中...' : '测试连接' }}
                </button>

                <!-- 测试结果 -->
                <div v-if="testResult" class="test-result" :class="{ success: testResult.success, error: !testResult.success }">
                  {{ testResult.success ? testResult.message : testResult.error }}
                  <div v-if="testResult.tables && testResult.tables.length" class="test-tables">
                    找到表格: {{ testResult.tables.join(', ') }}
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 弹窗底部 -->
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="$emit('close')">
              取消
            </button>
            <button class="btn btn-primary" @click="handleSave" :disabled="!canSave">
              保存配置
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, ref, watch, onMounted, onUnmounted } from 'vue'
import type { FeishuConfig, FeishuWorkspace } from '@/api'

/**
 * 飞书配置弹窗组件
 *
 * 用于配置飞书工作区连接信息
 * 支持两种格式：
 * 1. 新格式：全局 OAuth + 工作区特定配置
 * 2. 旧格式：每个工作区包含完整配置（向后兼容）
 */

// 定义 Props
const props = defineProps<{
  visible: boolean
  config: FeishuConfig | null
  testing: boolean
}>()

// 定义 Emits
const emit = defineEmits<{
  (e: 'close'): void
  (e: 'save', config: FeishuConfig): void
  (e: 'test', workspaceConfig: any): void
}>()

// 本地状态
const activeWorkspace = ref<string>(props.config?.active_workspace || 'default')
const localConfig = ref<FeishuConfig | null>(null)
const testResult = ref<{ success: boolean; message?: string; error?: string; tables?: string[] } | null>(null)

// 是否使用新格式（全局 OAuth）
const hasGlobalOAuth = computed(() => {
  return localConfig.value && 'oauth' in localConfig.value && !!localConfig.value.oauth
})

// 当前工作区配置
const currentWorkspace = computed<FeishuWorkspace | null>(() => {
  if (!localConfig.value) return null
  const name = activeWorkspace.value
  const workspace = localConfig.value.workspaces[name]
  return workspace || null
})

// 当前工作区名称
const currentWorkspaceName = computed(() => activeWorkspace.value)

// 全局 OAuth 令牌过期时间（新格式）
const globalTokenExpiry = computed(() => {
  if (!localConfig.value?.oauth?.token_expires_at) return null
  return new Date(localConfig.value.oauth.token_expires_at)
})

// 工作区令牌过期时间（旧格式）
const tokenExpiry = computed(() => {
  // 优先使用全局 OAuth 的过期时间
  if (globalTokenExpiry.value) return globalTokenExpiry.value
  // 旧格式：使用工作区级别的过期时间
  if (!currentWorkspace.value?.token_expires_at) return null
  return new Date(currentWorkspace.value.token_expires_at)
})

// 令牌是否有效
const isTokenValid = computed(() => {
  if (!tokenExpiry.value) return false
  return tokenExpiry.value > new Date()
})

// 是否可以测试
const canTest = computed(() => {
  if (hasGlobalOAuth.value) {
    // 新格式：检查全局 OAuth 和当前工作区的 base_url
    const oauth = localConfig.value?.oauth
    const ws = currentWorkspace.value
    return oauth && oauth.app_id && oauth.app_secret && ws && ws.base_url
  } else {
    // 旧格式：检查工作区级别的所有字段
    const ws = currentWorkspace.value
    return ws && ws.app_id && ws.app_secret && ws.base_url
  }
})

// 是否可以保存
const canSave = computed(() => {
  return localConfig.value && Object.keys(localConfig.value.workspaces).length > 0
})

// 监听 props 变化
watch(() => props.config, (newConfig) => {
  if (newConfig) {
    // 深拷贝配置，避免直接修改 props
    localConfig.value = {
      active_workspace: newConfig.active_workspace,
      workspaces: JSON.parse(JSON.stringify(newConfig.workspaces)),
      // 保留全局 OAuth 配置（如果有）
      ...(newConfig.oauth && { oauth: { ...newConfig.oauth } })
    }
    activeWorkspace.value = newConfig.active_workspace
  }
}, { immediate: true })

// 监听激活工作区变化
watch(activeWorkspace, () => {
  testResult.value = null
})

// OAuth 回调处理
const handleOAuthMessage = (event: MessageEvent) => {
  // 验证消息来源
  if (event.origin !== window.location.origin) return

  const { type, error, workspace, hasRefreshToken } = event.data

  if (type === 'feishu:oauth:success') {
    console.log('OAuth 授权成功:', { workspace, hasRefreshToken })
    // 刷新配置以获取新的 token
    window.location.reload()
  } else if (type === 'feishu:oauth:error') {
    console.error('OAuth 授权失败:', error)
    alert(`授权失败: ${error}`)
  }
}

// 组件挂载时添加消息监听器
onMounted(() => {
  window.addEventListener('message', handleOAuthMessage)
})

// 组件卸载时移除消息监听器
onUnmounted(() => {
  window.removeEventListener('message', handleOAuthMessage)
})

// 启动 OAuth 流程
const startOAuthFlow = () => {
  const frontendOrigin = window.location.origin
  const workspace = currentWorkspaceName.value || 'default'
  const authUrl = `/api/oauth/authorize?workspace=${encodeURIComponent(workspace)}&frontend_origin=${encodeURIComponent(frontendOrigin)}`
  window.open(authUrl, 'feishu-oauth', 'width=600,height=700')
}

// 格式化过期时间
const formatExpiry = (date: Date) => {
  return date.toLocaleString('zh-CN')
}

// 测试连接
function handleTest() {
  if (!currentWorkspace.value || !canTest.value) return

  testResult.value = null
  // 发送工作区名称，让后端使用已保存的配置进行测试
  // 这样可以避免发送被脱敏的 '***' 值
  emit('test', {
    workspace: activeWorkspace.value
  })
}

// 保存配置
function handleSave() {
  if (!localConfig.value) return

  // 更新激活工作区
  localConfig.value.active_workspace = activeWorkspace.value

  emit('save', localConfig.value)
}

// 外部测试结果监听
watch(() => props.testing, (isTesting) => {
  if (!isTesting && testResult.value === null) {
    // 如果测试结束但没有结果，可能是因为 emit 方式的问题
    // 实际使用中需要通过父组件传递测试结果
  }
})

// 暴露测试结果设置方法给父组件
defineExpose({
  setTestResult(result: any) {
    testResult.value = result
  },
  // 暴露刷新配置的方法，用于 OAuth 回调后更新
  async refreshConfig() {
    // 通知父组件重新加载配置
    window.location.reload()
  }
})
</script>

<style scoped>
/* 弹窗遮罩 */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s;
}

.modal-enter-active .modal-container,
.modal-leave-active .modal-container {
  transition: transform 0.3s, opacity 0.3s;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .modal-container,
.modal-leave-to .modal-container {
  transform: scale(0.95);
  opacity: 0;
}

/* 弹窗容器 */
.modal-container {
  background: white;
  border-radius: 16px;
  max-width: 600px;
  width: 100%;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.25);
}

/* 弹窗头部 */
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #f0f0f0;
}

.modal-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-main, #1a1a1a);
  margin: 0;
}

.modal-close {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  border: none;
  background: #f5f5f5;
  color: var(--text-sub, #666);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.modal-close:hover {
  background: #eee;
  color: var(--text-main, #1a1a1a);
}

/* 弹窗内容 */
.modal-content {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-main, #1a1a1a);
  margin: 0 0 16px 0;
}

/* 表单 */
.form-section {
  margin-bottom: 24px;
}

.oauth-section {
  background: #f8f9fa;
  padding: 16px;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.oauth-hint {
  margin-bottom: 16px;
  color: var(--text-sub, #666);
  font-size: 13px;
}

.form-label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-sub, #666);
  margin-bottom: 8px;
}

.form-input,
.form-select {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid #e5e5e5;
  border-radius: 8px;
  background: white;
  font-size: 14px;
  color: var(--text-main, #1a1a1a);
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.form-input:focus,
.form-select:focus {
  border-color: var(--primary, #ff2442);
  box-shadow: 0 0 0 2px rgba(255, 36, 66, 0.1);
}

.form-group {
  margin-bottom: 16px;
}

.form-hint {
  font-size: 12px;
  color: var(--text-placeholder, #999);
  margin: 4px 0 0 0;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

/* Token input group with authorize button */
.token-input-group {
  display: flex;
  gap: 8px;
}

.token-input-group .form-input {
  flex: 1;
}

.token-input-group .btn-secondary {
  white-space: nowrap;
  padding: 10px 16px;
}

/* Token status indicators */
.text-success {
  display: block;
  margin-top: 4px;
  font-size: 12px;
  color: #52c41a;
}

.text-warning {
  display: block;
  margin-top: 4px;
  font-size: 12px;
  color: #faad14;
}

/* 测试按钮 */
.test-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border-radius: 8px;
  border: 1px solid var(--primary, #ff2442);
  background: white;
  color: var(--primary, #ff2442);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.test-btn:hover:not(:disabled) {
  background: var(--primary, #ff2442);
  color: white;
}

.test-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.test-btn svg.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* 测试结果 */
.test-result {
  margin-top: 12px;
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 13px;
}

.test-result.success {
  background: #f6ffed;
  color: #52c41a;
  border: 1px solid #b7eb8f;
}

.test-result.error {
  background: #fff2f0;
  color: #ff4d4f;
  border: 1px solid #ffccc7;
}

.test-tables {
  margin-top: 8px;
  font-size: 12px;
  opacity: 0.9;
}

/* 弹窗底部 */
.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid #f0f0f0;
}

.btn {
  padding: 10px 24px;
  border-radius: 8px;
  border: none;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary {
  background: #f5f5f5;
  color: var(--text-sub, #666);
}

.btn-secondary:hover {
  background: #eee;
}

.btn-primary {
  background: var(--primary, #ff2442);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: var(--primary-hover, #e61e3a);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
