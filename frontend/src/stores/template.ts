// frontend/src/stores/template.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { ExtractedTemplate } from '@/types/template'

export type TemplateType = 'title' | 'structure' | 'visual' | 'composite'

export interface Template {
  id: string
  type: TemplateType
  name: string
  industry?: string
  pattern: string
  variables: string[]
  source_records: string[]
  usage_count: number
  created_at?: string
  description?: string
  examples?: string[]
  source_record_id?: string
  extracted_elements?: {
    title_template?: string
    structure_template?: string
    tone_style?: string
    cta_type?: string
  }
}

export interface TemplateState {
  templates: Template[]
  industries: string[]
  selectedType: TemplateType | 'all'
  selectedIndustry: string | null
  loading: boolean
}

export const useTemplateStore = defineStore('template', () => {
  // State
  const templates = ref<Template[]>([])
  const industries = ref<string[]>([])
  const selectedType = ref<TemplateType | 'all'>('all')
  const selectedIndustry = ref<string | null>(null)
  const loading = ref(false)

  // Getters
  const filteredTemplates = computed(() => {
    let results = templates.value

    if (selectedType.value !== 'all') {
      results = results.filter(t => t.type === selectedType.value)
    }

    if (selectedIndustry.value) {
      results = results.filter(t => t.industry === selectedIndustry.value)
    }

    return results.sort((a, b) => b.usage_count - a.usage_count)
  })

  const templatesByType = computed(() => {
    return {
      title: templates.value.filter(t => t.type === 'title'),
      structure: templates.value.filter(t => t.type === 'structure'),
      visual: templates.value.filter(t => t.type === 'visual')
    }
  })

  const hasTemplates = computed(() => templates.value.length > 0)

  // Actions
  async function loadTemplates() {
    loading.value = true
    try {
      const params = new URLSearchParams()
      if (selectedType.value !== 'all') {
        params.append('type', selectedType.value)
      }
      if (selectedIndustry.value) {
        params.append('industry', selectedIndustry.value)
      }

      const response = await fetch(`/api/templates?${params.toString()}`)
      const data = await response.json()

      if (data.success) {
        templates.value = data.data || []
        industries.value = [...new Set(templates.value
          .map(t => t.industry)
          .filter((i): i is string => Boolean(i))
        )]
      }
    } catch (error) {
      console.error('加载模板失败:', error)
      templates.value = []
    } finally {
      loading.value = false
    }
  }

  async function applyTemplate(templateId: string, context: {
    topic: string
    industry?: string
  }) {
    try {
      const response = await fetch('/api/templates/apply', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          template_id: templateId,
          context
        })
      })

      const data = await response.json()
      if (data.success) {
        // 更新使用次数
        const template = templates.value.find(t => t.id === templateId)
        if (template) {
          template.usage_count++
        }
        return data.data
      }
    } catch (error) {
      console.error('应用模板失败:', error)
    }
    return null
  }

  async function createTemplate(templateData: Omit<Template, 'id' | 'usage_count'>) {
    try {
      const response = await fetch('/api/templates', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(templateData)
      })

      const data = await response.json()
      if (data.success) {
        templates.value.push(data.data)
        return data.data
      }
    } catch (error) {
      console.error('创建模板失败:', error)
    }
    return null
  }

  async function deleteTemplate(templateId: string) {
    try {
      const response = await fetch(`/api/templates/${templateId}`, {
        method: 'DELETE'
      })

      const data = await response.json()
      if (data.success) {
        templates.value = templates.value.filter(t => t.id !== templateId)
        return true
      }
    } catch (error) {
      console.error('删除模板失败:', error)
    }
    return false
  }

  function setTypeFilter(type: TemplateType | 'all') {
    selectedType.value = type
  }

  function setIndustryFilter(industry: string | null) {
    selectedIndustry.value = industry
  }

  function getTemplateById(id: string): Template | undefined {
    return templates.value.find(t => t.id === id)
  }

  async function extractTemplate(recordId: string): Promise<ExtractedTemplate | null> {
    try {
      const response = await fetch('/api/templates/extract', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ record_id: recordId })
      })

      const data = await response.json()
      if (data.success) {
        return data.data
      }
    } catch (error) {
      console.error('提取模板失败:', error)
    }
    return null
  }

  return {
    // State
    templates,
    industries,
    selectedType,
    selectedIndustry,
    loading,
    // Getters
    filteredTemplates,
    templatesByType,
    hasTemplates,
    // Actions
    loadTemplates,
    applyTemplate,
    createTemplate,
    deleteTemplate,
    setTypeFilter,
    setIndustryFilter,
    getTemplateById,
    extractTemplate
  }
})
