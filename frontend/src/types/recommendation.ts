/**
 * 智能推荐类型定义 V2.0
 */

export type ScenarioType = 'beginner' | 'trending' | 'quality'

export type MatchLevel = 'high' | 'medium' | 'low'

export interface RecommendationRequest {
  topic: string
  industry?: string
  scenario?: ScenarioType
  limit?: number
}

export interface LearnableElements {
  hook: string      // 钩子类型
  structure: string // 结构框架
  tone: string      // 语言风格
  cta: string       // 互动设计
}

export interface RecommendationRecord {
  title: string
  cover_url: string
  cover_image?: string  // 兼容后端字段名
  industry: string
  metrics: {
    likes: number
    saves: number
    comments: number
    total_engagement: number
    save_ratio: number
  }
  follower_count: number
}

export interface RecommendationItem {
  record_id: string
  record: RecommendationRecord
  match_score: number
  match_level: MatchLevel
  recommend_reasons: string[]
  learnable_elements: LearnableElements
}

export interface RecommendationResponse {
  success: boolean
  data: {
    topic: string
    scenario?: ScenarioType
    total: number
    results: RecommendationItem[]
  }
}

// 缓存管理相关
export interface ClearCacheRequest {
  target?: 'all' | 'expired' | 'record'
  record_id?: string
  older_than_days?: number
}

export interface ClearCacheResponse {
  success: boolean
  data: {
    cleared_count: number
  }
}

export interface CacheStatsResponse {
  success: boolean
  data: {
    total_entries: number
    expired_entries: number
    hit_rate?: number
  }
}
