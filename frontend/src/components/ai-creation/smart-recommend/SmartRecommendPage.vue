<template>
  <div class="smart-recommend-page">
    <RecommendInput
      @search="handleSearch"
    />

    <RecommendResult
      :recommendations="recommendationStore.recommendations"
      :loading="recommendationStore.loading"
      :search-topic="recommendationStore.searchTopic"
      @view-detail="handleViewDetail"
      @apply="handleApply"
    />
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useRecommendationStore } from '@/stores/recommendation'
import RecommendInput from './RecommendInput.vue'
import RecommendResult from './RecommendResult.vue'

const router = useRouter()
const recommendationStore = useRecommendationStore()

async function handleSearch(topic: string, scenario?: string) {
  await recommendationStore.fetchRecommendations(topic, { scenario })
}

function handleViewDetail(record: any) {
  router.push({ name: 'reference', query: { id: record.record_id } })
}

function handleApply(record: any) {
  router.push({
    name: 'QuickCreate',
    query: { reference: record.record_id }
  })
}
</script>

<style scoped>
.smart-recommend-page {
  padding: 0;
}
</style>
