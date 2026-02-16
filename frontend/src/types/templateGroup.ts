/**
 * 模板组类型定义
 */

export type TemplateElementType = 'title' | 'structure' | 'tone' | 'cta'

export interface TemplateElement {
  id: string
  type: TemplateElementType
  name: string
  description: string
  content: string
  examples: string[]
  usage_count: number
  created_at: string
}

export interface TemplateGroup {
  group_id: string
  source_record_id: string
  source_title: string
  source_industry?: string
  source_cover?: string
  match_score?: number
  saved_at: string
  elements: TemplateElement[]
}

export interface CreateTemplateGroupRequest {
  source_record_id: string
  source_title: string
  source_industry?: string
  source_cover?: string
  match_score?: number
  elements: Array<{
    type: TemplateElementType
    name: string
    description: string
    content: string
    examples?: string[]
  }>
}

export interface CreateTemplateGroupResponse {
  success: boolean
  data: {
    group_id: string
  }
}

export interface ListTemplateGroupsResponse {
  success: boolean
  data: TemplateGroup[]
}

export interface ElementTypeFilterOption {
  value: 'all' | TemplateElementType
  label: string
}

export interface SortOption {
  value: 'saved_at' | 'usage_count' | 'match_score'
  label: string
}
