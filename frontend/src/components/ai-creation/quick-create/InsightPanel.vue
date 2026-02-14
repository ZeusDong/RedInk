<template>
  <div class="insight-panel">
    <div class="panel-header">
      <h3>📊 对标洞察</h3>
      <button @click="togglePanel" class="toggle-btn">
        {{ expanded ? '收起' : '展开' }}
      </button>
    </div>

    <div v-if="expanded" class="panel-body">
      <!-- 行业筛选 -->
      <div class="industry-filter">
        <label>当前行业：</label>
        <select v-model="selectedIndustry" @change="loadInsights" class="industry-select">
          <option value="">自动推断</option>
          <option v-for="ind in industries" :key="ind" :value="ind">
            {{ ind }}
          </option>
        </select>
      </div>

      <!-- AI 总结列表 -->
      <div v-if="filteredSummaries.length > 0" class="insight-section">
        <h4>📝 AI 总结</h4>
        <div class="summary-list">
          <InsightCard
            v-for="summary in filteredSummaries"
            :key="summary.id"
            :insight="summary"
            type="summary"
            :is-selected="selectedInsights.has(`summary-${summary.id}`)"
            @select="handleSelectSummary"
            @deselect="handleDeselectSummary"
          />
        </div>
      </div>

      <!-- 高表现笔记推荐 -->
      <div v-if="filteredTopRecords.length > 0" class="insight-section">
        <h4>🔥 高表现笔记</h4>
        <div class="record-list">
          <InsightCard
            v-for="record in filteredTopRecords"
            :key="record.record_id"
            :insight="record"
            type="record"
            :is-selected="selectedInsights.has(`record-${record.record_id}`)"
            @select="handleSelectRecord"
            @deselect="handleDeselectRecord"
          />
        </div>
      </div>

      <!-- 空状态 -->
      <div v-if="!loading && filteredSummaries.length === 0 && filteredTopRecords.length === 0" class="empty-state">
        <p>暂无相关洞察，请先完成对标分析</p>
        <RouterLink to="/analysis" class="link">前往分析 →</RouterLink>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading" class="loading-state">
        <p>加载中...</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import InsightCard from './InsightCard.vue'

interface Summary {
  id: string
  content: string
  record_count: number
  industry: string
}

interface ReferenceRecord {
  record_id: string
  title: string
  industry?: string
  metrics?: {
    likes?: number
    saves?: number
    total_engagement?: number
  }
}

const expanded = ref(false)
const loading = ref(false)
const selectedIndustry = ref('')
const selectedInsights = ref<Set<string>>(new Set())

// 模拟数据 - 实际应从 store 获取
const industries = ref<string[]>(['美妆护肤', '美食', '旅行', '健身', '数码'])
const summaries = ref<Summary[]>([])
const topRecords = ref<ReferenceRecord[]>([])

const emit = defineEmits<{
  applyInsight: [payload: { type: 'summary' | 'record'; data: Summary | ReferenceRecord }]
}>()

function togglePanel() {
  expanded.value = !expanded.value
  if (expanded.value) {
    loadInsights()
  }
}

async function loadInsights() {
  loading.value = true
  try {
    // TODO: 实际应从 store 加载数据
    // await summaryStore.loadSummaries()
    // await analysisStore.loadCompletedRecords()

    // 模拟数据加载
    summaries.value = [
      {
        id: '1',
        content: '美妆护肤类内容在春季应重点关注防晒和保湿主题，用户对成分透明的产品更感兴趣。',
        record_count: 15,
        industry: '美妆护肤'
      }
    ]

    topRecords.value = [
      {
        record_id: 'rec1',
        title: '春季护肤必备清单',
        industry: '美妆护肤',
        metrics: {
          likes: 15000,
          saves: 8000,
          total_engagement: 25000
        }
      }
    ]
  } finally {
    loading.value = false
  }
}

function handleSelectSummary(summary: Summary) {
  selectedInsights.value.add(`summary-${summary.id}`)
  emit('applyInsight', { type: 'summary', data: summary })
}

function handleDeselectSummary(summary: Summary) {
  selectedInsights.value.delete(`summary-${summary.id}`)
}

function handleSelectRecord(record: ReferenceRecord) {
  selectedInsights.value.add(`record-${record.record_id}`)
  emit('applyInsight', { type: 'record', data: record })
}

function handleDeselectRecord(record: ReferenceRecord) {
  selectedInsights.value.delete(`record-${record.record_id}`)
}

// 过滤后的总结
const filteredSummaries = computed(() => {
  let results = summaries.value
  if (selectedIndustry.value) {
    results = results.filter(s => s.industry === selectedIndustry.value)
  }
  return results.slice(0, 5)
})

// 过滤后的记录
const filteredTopRecords = computed(() => {
  let records = [...topRecords.value]
  if (selectedIndustry.value) {
    records = records.filter(r => r.industry === selectedIndustry.value)
  }
  // 按互动量排序
  return records
    .sort((a, b) => (b.metrics?.total_engagement || 0) - (a.metrics?.total_engagement || 0))
    .slice(0, 5)
})
</script>

<style scoped>
.insight-panel {
  background: white;
  border: 1px solid #e8e6e3;
  border-radius: 12px;
  margin-top: 16px;
  overflow: hidden;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #e8e6e3;
}

.panel-header h3 {
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.toggle-btn {
  padding: 6px 12px;
  border: 1px solid #e0dedb;
  border-radius: 6px;
  background: white;
  color: #666;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.toggle-btn:hover {
  border-color: var(--primary, #ff2442);
  color: var(--primary, #ff2442);
}

.panel-body {
  padding: 16px;
}

.industry-filter {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0efed;
}

.industry-filter label {
  font-size: 13px;
  color: #666;
}

.industry-select {
  flex: 1;
  padding: 6px 12px;
  border: 1px solid #e0dedb;
  border-radius: 6px;
  background: white;
  font-size: 13px;
  color: #333;
}

.industry-select:focus {
  outline: none;
  border-color: var(--primary, #ff2442);
}

.insight-section {
  margin-bottom: 20px;
}

.insight-section:last-child {
  margin-bottom: 0;
}

.insight-section h4 {
  font-size: 13px;
  font-weight: 600;
  color: #333;
  margin: 0 0 12px 0;
}

.summary-list,
.record-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.empty-state {
  text-align: center;
  padding: 32px 16px;
  color: #999;
}

.empty-state p {
  font-size: 13px;
  margin: 0 0 12px 0;
}

.link {
  color: var(--primary, #ff2442);
  font-size: 13px;
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}

.loading-state {
  text-align: center;
  padding: 32px 16px;
  color: #999;
}

.loading-state p {
  font-size: 13px;
  margin: 0;
}
</style>
