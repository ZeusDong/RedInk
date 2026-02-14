<template>
  <nav class="page-navigation">
    <RouterLink
      v-for="tab in tabs"
      :key="tab.key"
      :to="`/ai-creation/${tab.key}`"
      class="nav-tab"
      :class="{ active: currentTab === tab.key }"
    >
      <span class="tab-icon">{{ tab.icon }}</span>
      <span class="tab-label">{{ tab.label }}</span>
    </RouterLink>
  </nav>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const tabs = [
  { key: 'create', icon: '📑', label: '快速创作' },
  { key: 'recommend', icon: '💡', label: '智能推荐' },
  { key: 'templates', icon: '📋', label: '模板库' },
  { key: 'optimize', icon: '✨', label: '内容优化' }
]

const currentTab = computed(() => {
  const match = route.path.match(/\/ai-creation\/([^/]+)/)
  return match ? match[1] : 'create'
})
</script>

<style scoped>
.page-navigation {
  display: flex;
  gap: 4px;
  padding: 4px;
  background: #f8f7f5;
  border-radius: 12px;
  margin-bottom: 24px;
}

.nav-tab {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 16px;
  border-radius: 10px;
  text-decoration: none;
  color: #666;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s ease;
  cursor: pointer;
}

.nav-tab:hover {
  background: rgba(255, 255, 255, 0.5);
  color: #333;
}

.nav-tab.active {
  background: white;
  color: var(--primary, #ff2442);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.tab-icon {
  font-size: 18px;
}

.tab-label {
  font-size: 14px;
}
</style>
