/**
 * Unified note record interface for both benchmark and search sources
 */
export interface NoteRecord {
  record_id: string
  // Display fields (computed)
  display_title: string
  cover_url: string
  // Mode-specific fields
  is_benchmark_mode: boolean
  search_keyword?: string  // Only for search mode
  is_target_for_creation?: boolean  // Only for benchmark mode
  // Common fields
  blogger: string
  blogger_avatar?: string
  metrics: {
    likes: number
    saves: number
    comments: number
  }
  note_link?: string
  // Raw fields for reference
  raw_title?: string
  raw_body?: string
}

/**
 * Data source mode
 */
export type NoteSourceMode = 'benchmark' | 'search'

/**
 * Workspace configuration for note sources
 */
export interface NoteWorkspaceConfig {
  name: string
  label: string
  workspace_param: string
  icon: string
}
