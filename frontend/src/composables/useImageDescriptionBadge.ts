/**
 * Image Description Badge Composable
 *
 * Composable for managing image description badge states
 */

import { computed, ref, type Ref, watch } from 'vue'
import type { ImageDescription, BadgeState } from '@/types/analysis'

export interface BadgeStateOptions {
  imageDescriptions: Ref<Record<number, ImageDescription>>
  visualDescription: Ref<string> | string  // Accept both Ref and string for flexibility
}

export interface BadgeStateReturn {
  getBadgeState: (index: number) => BadgeState
  getBadgeIcon: (state: BadgeState) => string
  getBadgeTitle: (state: BadgeState) => string
  generatedImageIndices: Ref<Set<number>>
  visualDescValue: Ref<string>  // Expose the tracked value for debugging
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

  // Create a ref to track the current description value for reactivity
  const visualDescValue = ref(
    typeof visualDescription === 'string' ? visualDescription : visualDescription.value
  )

  // Watch for changes if visualDescription is a Ref
  if (typeof visualDescription !== 'string') {
    watch(visualDescription, (newVal) => {
      visualDescValue.value = newVal
    }, { immediate: true })
  }

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

    // Get this image's unique ID marker format: <!-- DESC-${uniqueId} -->
    // Note: desc.id already includes the index suffix (e.g., "xxx-1" for cover, "xxx-0" for image 1)
    // So we only need to check for DESC-${desc.id}, no need to add -${idx} again
    const idMarker = `<!-- DESC-${desc.id} -->`

    // Check if this specific image's ID marker exists in form
    const isStillInForm = visualDescValue.value.includes(idMarker)

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
    generatedImageIndices,
    visualDescValue
  }
}
