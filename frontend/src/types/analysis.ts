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
 * Index convention:
 * -1 = cover image (封面图)
 * 0, 1, 2... = content images (内容图)
 */
export type ImageIndex = number
