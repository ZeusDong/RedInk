/**
 * 模板类型定义
 */

import type { TemplateType } from '@/stores/template'

export interface ExtractedTemplateElement {
  type: 'title' | 'structure' | 'tone' | 'cta'
  name: string
  description: string
  selected: boolean
}

export interface ExtractedTemplate {
  suggested_name: string
  title_template?: string
  structure_template?: string
  tone_style?: string
  cta_type?: string
  elements: ExtractedTemplateElement[]
}

export interface ExtractTemplateRequest {
  record_id: string
}

export interface ExtractTemplateResponse {
  success: boolean
  data: ExtractedTemplate
}

export interface CreateTemplateRequest {
  name: string
  industry: string
  type: TemplateType
  description?: string
  source_record_id?: string
  extracted_elements?: {
    title_template?: string
    structure_template?: string
    tone_style?: string
    cta_type?: string
  }
}
