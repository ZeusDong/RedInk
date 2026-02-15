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
import type { ScenarioType } from '@/types/recommendation'

const router = useRouter()
const recommendationStore = useRecommendationStore()

async function handleSearch(topic: string, scenario?: ScenarioType) {
  await recommendationStore.fetchRecommendations(topic, {
    scenario,
    limit: 20
  })
}

function handleViewDetail(recordId: string) {
  router.push({ name: 'reference', query: { record: recordId } })
}

function handleApply(recordId: string) {
  router.push({
    name: 'QuickCreate',
    query: { reference: recordId }
  })
}
</script>

<style scoped>
.smart-recommend-page {
  padding: 0;
}
</style>
