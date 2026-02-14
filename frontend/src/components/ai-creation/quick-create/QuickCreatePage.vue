<template>
  <div class="quick-create-page">
    <div class="create-container">
      <!-- 创作输入区 -->
      <div class="composer-section">
        <ComposerInput
          v-model="topicInput"
          :loading="generating"
          @generate="handleGenerate"
          @images-change="handleImagesChange"
        />
      </div>

      <!-- 对标洞察面板 -->
      <InsightPanel
        :insight-selections="insightSelections"
        @toggle-insight="toggleInsight"
      />

      <!-- 已应用的洞察 -->
      <div v-if="selectedInsights.length > 0" class="applied-insights">
        <h4 class="section-title">已应用的洞察</h4>
        <div class="insight-tags">
          <span
            v-for="(insight, idx) in selectedInsights"
            :key="idx"
            class="insight-tag"
          >
            {{ insight.type === 'summary' ? '📝' : '📄' }}
            {{ getInsightTitle(insight) }}
            <button @click="removeInsight(idx)" class="remove-tag">×</button>
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useGeneratorStore } from '@/stores/generator'
import ComposerInput from '@/components/home/ComposerInput.vue'
import InsightPanel from './InsightPanel.vue'

interface AppliedInsight {
  type: 'summary' | 'record'
  data: any
}

const router = useRouter()
const generatorStore = useGeneratorStore()
const topicInput = ref('')
const generating = ref(false)
const selectedInsights = ref<AppliedInsight[]>([])
const insightSelections = ref<Set<string>>(new Set())

function handleGenerate() {
  if (!topicInput.value.trim()) return

  generating.value = true

  // 调用生成 API，传递 insights
  generateOutline()
}

async function generateOutline() {
  try {
    const response = await fetch('/api/outline', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        topic: topicInput.value.trim(),
        reference_records: selectedInsights.value.map(i => i.data)
      })
    })

    const data = await response.json()
    if (data.success) {
      // 保存到generator store
      generatorStore.setTopic(topicInput.value.trim())
      generatorStore.setOutline(data.outline || '', data.pages || [])

      // 跳转到大纲页面
      router.push({ name: 'outline' })
    } else {
      console.error('生成失败:', data.error)
      alert(data.error || '生成失败，请重试')
    }
  } catch (error) {
    console.error('生成异常:', error)
    alert('生成失败，请重试')
  } finally {
    generating.value = false
  }
}

function handleImagesChange(images: File[]) {
  console.log('Images changed:', images)
  // TODO: 处理参考图片
}

function toggleInsight(payload: { type: 'summary' | 'record'; data: any }) {
  const key = `${payload.type}-${payload.type === 'summary' ? payload.data.id : payload.data.record_id}`

  if (insightSelections.value.has(key)) {
    // Deselect: remove from both selection tracking and applied list
    insightSelections.value.delete(key)
    const idx = selectedInsights.value.findIndex(i =>
      i.type === payload.type &&
      (payload.type === 'summary' ? i.data.id === payload.data.id : i.data.record_id === payload.data.record_id)
    )
    if (idx !== -1) {
      selectedInsights.value.splice(idx, 1)
    }
  } else {
    // Select: add to both selection tracking and applied list
    insightSelections.value.add(key)
    selectedInsights.value.push(payload)
  }
}

function removeInsight(index: number) {
  const removed = selectedInsights.value[index]
  const key = `${removed.type}-${removed.type === 'summary' ? removed.data.id : removed.data.record_id}`
  insightSelections.value.delete(key)
  selectedInsights.value.splice(index, 1)
}

function getInsightTitle(insight: AppliedInsight): string {
  if (insight.type === 'summary') {
    return insight.data.industry || 'AI总结'
  }
  return insight.data.title || '对标笔记'
}
</script>

<style scoped>
.quick-create-page {
  max-width: 800px;
  margin: 0 auto;
}

.create-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.composer-section {
  width: 100%;
}

.applied-insights {
  background: white;
  border-radius: 12px;
  padding: 16px;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin: 0 0 12px 0;
}

.insight-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.insight-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: rgba(255, 36, 66, 0.1);
  border-radius: 20px;
  font-size: 13px;
  color: var(--primary, #ff2442);
}

.remove-tag {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  border: none;
  background: var(--primary, #ff2442);
  color: white;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
}

.remove-tag:hover {
  opacity: 0.8;
}
</style>
