<template>
  <div v-if="reasons.length > 0" class="recommend-reasons">
    <div class="reasons-header">
      <span class="header-icon">✨</span>
      <span class="header-title">推荐理由</span>
    </div>
    <ul class="reasons-list">
      <li v-for="(reason, index) in reasons" :key="index" class="reason-item">
        <span class="reason-bullet">{{ index + 1 }}</span>
        <span class="reason-text">{{ reason }}</span>
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
interface Props {
  reasons: string[]
}

defineProps<Props>()
</script>

<style scoped>
.recommend-reasons {
  padding: 12px;
  background: linear-gradient(135deg, rgba(255, 36, 66, 0.03) 0%, rgba(255, 152, 0, 0.03) 100%);
  border-radius: 8px;
  border: 1px solid rgba(255, 36, 66, 0.1);
}

.reasons-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 10px;
  font-size: 13px;
  font-weight: 600;
  color: var(--primary, #ff2442);
}

.header-icon {
  font-size: 14px;
}

.header-title {
  line-height: 1;
}

.reasons-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.reason-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.reason-bullet {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  background: var(--primary, #ff2442);
  color: white;
  border-radius: 50%;
  font-size: 11px;
  font-weight: 600;
  line-height: 1;
}

.reason-text {
  flex: 1;
  font-size: 13px;
  color: #333;
  line-height: 1.5;
}
</style>
