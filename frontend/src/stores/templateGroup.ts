// frontend/src/stores/templateGroup.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type {
  TemplateGroup,
  TemplateElement,
  TemplateElementType
} from '@/types/templateGroup'

export const useTemplateGroupStore = defineStore('templateGroup', () => {
  // State
  const groups = ref<TemplateGroup[]>([])
  const loading = ref(false)
  const selectedType = ref<'all' | TemplateElementType>('all')
  const searchQuery = ref('')
  const sortBy = ref<'saved_at' | 'usage_count' | 'match_score'>('saved_at')

  // Getters
  const filteredGroups = computed(() => {
    let results = [...groups.value]

    // 类型筛选
    if (selectedType.value !== 'all') {
      results = results.filter(group =>
        group.elements.some(e => e.type === selectedType.value)
      )
      // 同时过滤掉不匹配的元素
      results = results.map(group => ({
        ...group,
        elements: group.elements.filter(e =>
          selectedType.value === 'all' || e.type === selectedType.value
        )
      }))
    }

    // 搜索筛选
    if (searchQuery.value.trim()) {
      const query = searchQuery.value.toLowerCase().trim()
      results = results.filter(group => {
        const titleMatch = group.source_title.toLowerCase().includes(query)
        const industryMatch = (group.source_industry || '').toLowerCase().includes(query)
        const elementsMatch = group.elements.some(e =>
          e.name.toLowerCase().includes(query) ||
          e.description.toLowerCase().includes(query)
        )
        return titleMatch || industryMatch || elementsMatch
      })
    }

    // 排序
    if (sortBy.value === 'usage_count') {
      results.sort((a, b) => {
        const countA = a.elements.reduce((sum, e) => sum + e.usage_count, 0)
        const countB = b.elements.reduce((sum, e) => sum + e.usage_count, 0)
        return countB - countA
      })
    } else if (sortBy.value === 'match_score') {
      results.sort((a, b) => (b.match_score || 0) - (a.match_score || 0))
    } else {
      results.sort((a, b) => b.saved_at.localeCompare(a.saved_at))
    }

    return results
  })

  const hasGroups = computed(() => groups.value.length > 0)

  // Actions
  async function loadGroups() {
    loading.value = true
    try {
      const params = new URLSearchParams()
      if (selectedType.value !== 'all') {
        params.append('type', selectedType.value)
      }
      if (searchQuery.value) {
        params.append('search', searchQuery.value)
      }
      if (sortBy.value) {
        params.append('sort_by', sortBy.value)
      }

      const response = await fetch(`/api/template-groups?${params.toString()}`)
      const data = await response.json()

      if (data.success) {
        groups.value = data.data || []
      }
    } catch (error) {
      console.error('加载模板组失败:', error)
      groups.value = []
    } finally {
      loading.value = false
    }
  }

  async function deleteGroup(groupId: string) {
    try {
      const response = await fetch(`/api/template-groups/${groupId}`, {
        method: 'DELETE'
      })

      const data = await response.json()
      if (data.success) {
        groups.value = groups.value.filter(g => g.group_id !== groupId)
        return true
      }
    } catch (error) {
      console.error('删除模板组失败:', error)
    }
    return false
  }

  async function deleteElement(groupId: string, elementId: string) {
    try {
      const response = await fetch(`/api/template-groups/${groupId}/elements/${elementId}`, {
        method: 'DELETE'
      })

      const data = await response.json()
      if (data.success) {
        // 更新本地数据
        const group = groups.value.find(g => g.group_id === groupId)
        if (group) {
          group.elements = group.elements.filter(e => e.id !== elementId)
        }
        return true
      }
    } catch (error) {
      console.error('删除技巧失败:', error)
    }
    return false
  }

  async function applyElement(groupId: string, elementId: string) {
    try {
      const response = await fetch(`/api/template-groups/${groupId}/elements/${elementId}/apply`, {
        method: 'POST'
      })

      const data = await response.json()
      if (data.success) {
        // 更新本地使用次数
        const group = groups.value.find(g => g.group_id === groupId)
        if (group) {
          const element = group.elements.find(e => e.id === elementId)
          if (element) {
            element.usage_count++
          }
        }
        return true
      }
    } catch (error) {
      console.error('应用技巧失败:', error)
    }
    return false
  }

  async function createGroup(data: {
    source_record_id: string
    source_title: string
    source_industry?: string
    source_cover?: string
    match_score?: number
    elements: Array<{
      type: 'title' | 'structure' | 'tone' | 'cta'
      name: string
      description: string
      content: string
      examples?: string[]
    }>
  }) {
    try {
      const response = await fetch('/api/template-groups', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
      })

      const result = await response.json()
      if (result.success) {
        // 重新加载列表
        await loadGroups()
        return result.data
      }
    } catch (error) {
      console.error('创建模板组失败:', error)
    }
    return null
  }

  async function extractTemplateGroup(recordId: string) {
    try {
      const response = await fetch('/api/templates/extract', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ record_id: recordId })
      })

      const data = await response.json()
      if (data.success) {
        return data.data
      }
    } catch (error) {
      console.error('提取模板组失败:', error)
    }
    return null
  }

  function setTypeFilter(type: 'all' | TemplateElementType) {
    selectedType.value = type
  }

  function setSearchQuery(query: string) {
    searchQuery.value = query
  }

  function setSortBy(sort: 'saved_at' | 'usage_count' | 'match_score') {
    sortBy.value = sort
  }

  function getGroupById(id: string): TemplateGroup | undefined {
    return groups.value.find(g => g.group_id === id)
  }

  function getElementById(groupId: string, elementId: string): TemplateElement | undefined {
    const group = groups.value.find(g => g.group_id === groupId)
    return group?.elements.find(e => e.id === elementId)
  }

  return {
    // State
    groups,
    loading,
    selectedType,
    searchQuery,
    sortBy,
    // Getters
    filteredGroups,
    hasGroups,
    // Actions
    loadGroups,
    deleteGroup,
    deleteElement,
    applyElement,
    createGroup,
    extractTemplateGroup,
    setTypeFilter,
    setSearchQuery,
    setSortBy,
    getGroupById,
    getElementById
  }
})
