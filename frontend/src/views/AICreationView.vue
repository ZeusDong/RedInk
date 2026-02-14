<template>
  <div class="ai-creation-view">
    <header class="top-header">
      <div class="header-left">
        <h1 class="page-title">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"></path>
          </svg>
          AI 创作
        </h1>
      </div>
      <div class="header-right">
        <p class="page-subtitle">智能内容创作工作台</p>
      </div>
    </header>

    <PageNavigation />

    <main class="page-content">
      <RouterView v-slot="{ Component }">
        <component :is="Component" />
      </RouterView>
    </main>
  </div>
</template>

<script setup lang="ts">
import { RouterView } from 'vue-router'
import PageNavigation from '@/components/ai-creation/PageNavigation.vue'
</script>

<style scoped>
.ai-creation-view {
  min-height: 100vh;
  background: #f8f7f5;
  display: flex;
  flex-direction: column;
}

.top-header {
  position: sticky;
  top: 0;
  z-index: 100;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 32px;
  height: 64px;
  background: white;
  border-bottom: 1px solid #e8e6e3;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 20px;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0;
}

.page-title svg {
  color: var(--primary, #ff2442);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.page-subtitle {
  font-size: 14px;
  color: #666;
  margin: 0;
}

.page-content {
  flex: 1;
  padding: 24px 32px;
  overflow-y: auto;
}
</style>
