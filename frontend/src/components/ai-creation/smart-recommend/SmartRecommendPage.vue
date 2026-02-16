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
      @save-template="handleSaveTemplate"
    />

    <SaveAsTemplateModal
      :visible="showSaveModal"
      :record-id="selectedRecordId"
      :record="selectedRecord"
      @close="showSaveModal = false"
      @saved="handleTemplateSaved"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useRecommendationStore } from '@/stores/recommendation'
import RecommendInput from './RecommendInput.vue'
import RecommendResult from './RecommendResult.vue'
import SaveAsTemplateModal from './SaveAsTemplateModal.vue'
import type { ScenarioType, RecommendationItem } from '@/types/recommendation'

const router = useRouter()
const recommendationStore = useRecommendationStore()

const showSaveModal = ref(false)
const selectedRecordId = ref('')
const selectedRecord = ref<any>(null)

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

function handleSaveTemplate(recordId: string, record: any) {
  // 找到完整的 recommendation item 来获取 match_score
  const fullItem = recommendationStore.recommendations.find(
    (item: RecommendationItem) => item.record_id === recordId
  )

  selectedRecordId.value = recordId
  selectedRecord.value = {
    ...record,
    match_score: fullItem?.match_score
  }
  showSaveModal.value = true
}

function handleTemplateSaved(templateId: string) {
  // Optionally show a success message
  console.log('Template saved:', templateId)
}
</script>

<style scoped>
.smart-recommend-page {
  padding: 0;
}
</style>
