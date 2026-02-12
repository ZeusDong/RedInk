/**
 * Analysis type definitions
 *
 * Types for image description badge feature and analysis draft management
 */

/**
 * Description metadata for a single image
 */
export interface ImageDescription {
  id: string        // Unique ID for this description (used for tracking)
  content: string   // The description text content
}

/**
 * Extended draft data with image description tracking
 * Works alongside the existing AnalysisDraft interface in api/analysis.ts
 */
export interface ImageDescriptionDraft {
  generated_image_indices: number[]           // Which image indices have generated descriptions
  image_descriptions: Record<number, ImageDescription>  // Map of index -> description metadata
}

/**
 * Badge state for an image
 */
export type BadgeState = 'none' | 'generated' | 'missing'

/**
 * Sub-comment (reply) within a top comment
 */
export interface SubComment {
  id: string          // Unique identifier for v-for key
  content: string      // Comment content
  likes?: number       // Optional like count
  is_blogger: boolean  // Whether this is the blogger's reply
}

/**
 * Top-level comment with optional sub-comments
 */
export interface Comment {
  id: string                    // Unique identifier for v-for key
  content: string               // Comment content
  likes?: number                // Optional like count
  sub_comments?: SubComment[]   // Optional array of sub-comments
}

/**
 * Index convention:
 * -1 = cover image (封面图)
 * 0, 1, 2... = content images (内容图)
 */
export type ImageIndex = number
