/**
 * Image Description Badge Composable
 *
 * Composable for managing image description badge states
 */

import { computed, ref, type Ref } from 'vue'
import type { ImageDescription, BadgeState } from '@/types/analysis'

export interface BadgeStateOptions {
  imageDescriptions: Ref<Record<number, ImageDescription>>
  visualDescription: Ref<string>
}

export interface BadgeStateReturn {
  getBadgeState: (index: number) => BadgeState
  getBadgeIcon: (state: BadgeState) => string
  getBadgeTitle: (state: BadgeState) => string
  generatedImageIndices: Ref<Set<number>>
}

/**
 * Composable for managing image description badge states
 *
 * @param options - Configuration containing image descriptions and form content
 * @returns Badge state utilities
 */
export function useImageDescriptionBadge(
  options: BadgeStateOptions
): BadgeStateReturn {
  const { imageDescriptions, visualDescription } = options

  // Computed set of indices that have generated descriptions
  const generatedImageIndices = computed(() => {
    return new Set(
      Object.keys(imageDescriptions.value).map(k => Number(k))
    )
  })

  /**
   * Get the badge state for a specific image index
   * @param idx - Image index (-1 for cover, 0+ for content images)
   * @returns Current badge state
   */
  function getBadgeState(idx: number): BadgeState {
    const desc = imageDescriptions.value[idx]
    if (!desc) return 'none'

    // Check if description is still in the form by ID marker
    const idMarker = `<!-- DESC-${desc.id} -->`
    const isStillInForm = visualDescription.value.includes(idMarker)

    return isStillInForm ? 'generated' : 'missing'
  }

  /**
   * Get the icon character for a badge state
   * @param state - Badge state
   * @returns Icon character (✓, ⚠️, or empty)
   */
  function getBadgeIcon(state: BadgeState): string {
    if (state === 'generated') return '✓'
    if (state === 'missing') return '⚠️'
    return ''
  }

  /**
   * Get the tooltip title for a badge state
   * @param state - Badge state
   * @returns Tooltip text (Chinese)
   */
  function getBadgeTitle(state: BadgeState): string {
    if (state === 'generated') return '描述已生成'
    if (state === 'missing') return '描述内容已缺失，建议重新生成'
    return ''
  }

  return {
    getBadgeState,
    getBadgeIcon,
    getBadgeTitle,
    generatedImageIndices
  }
}
