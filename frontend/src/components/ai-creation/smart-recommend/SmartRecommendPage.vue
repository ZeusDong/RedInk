<template>
  <div class="smart-recommend-page">
    <RecommendInput
      @search="handleSearch"
    />

    <RecommendResult
      :recommendations="recommendations"
      :loading="loading"
      :search-topic="searchTopic"
      @view-detail="handleViewDetail"
      @apply="handleApply"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import RecommendInput from './RecommendInput.vue'
import RecommendResult from './RecommendResult.vue'

interface ReferenceRecord {
  record_id: string
  title: string
  cover_url: string
  images_count?: number
  industry?: string
  note_type?: string
  metrics?: {
    likes?: number
    saves?: number
    comments?: number
  }
}

interface RecommendationItem {
  record: ReferenceRecord
  match_score: number
  reasons?: string[]
}

const router = useRouter()
const recommendations = ref<RecommendationItem[]>([])
const loading = ref(false)
const searchTopic = ref('')

async function handleSearch(topic: string, scenario?: string) {
  searchTopic.value = topic
  loading.value = true

  // Log scenario for future use
  if (scenario) {
    console.log('Search scenario:', scenario)
  }

  try {
    // TODO: Call backend API
    // const response = await fetch('/api/recommend', {
    //   method: 'POST',
    //   headers: { 'Content-Type': 'application/json' },
    //   body: JSON.stringify({ topic, scenario })
    // })
    // const data = await response.json()

    // Simulated data for now
    await new Promise(resolve => setTimeout(resolve, 1000))

    recommendations.value = [
      {
        record: {
          record_id: 'rec1',
          title: `${topic} - 实用技巧分享`,
          cover_url: 'https://via.placeholder.com/300x400',
          images_count: 4,
          industry: '生活',
          note_type: '图文',
          metrics: {
            likes: 15000,
            saves: 8000,
            comments: 1200
          }
        },
        match_score: 0.85,
        reasons: ['industry', 'keyword']
      }
    ]
  } finally {
    loading.value = false
  }
}

function handleViewDetail(record: ReferenceRecord) {
  // Navigate to detail view
  router.push({ name: 'reference', query: { id: record.record_id } })
}

function handleApply(record: ReferenceRecord) {
  // Navigate to quick create with record applied
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
