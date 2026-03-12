/**
 * Canvas Utilities
 */

/**
 * Calculate zoom scale to fit image in container
 */
export function calculateFitScale(containerWidth, containerHeight, imageWidth, imageHeight) {
  const scaleX = containerWidth / imageWidth
  const scaleY = containerHeight / imageHeight
  return Math.min(scaleX, scaleY)
}

/**
 * Clamp zoom level between min and max
 */
export function clampZoom(zoom, min = 0.1, max = 5) {
  return Math.max(min, Math.min(max, zoom))
}

/**
 * Format zoom as percentage string
 */
export function formatZoomPercent(zoom) {
  return `${Math.round(zoom * 100)}%`
}
