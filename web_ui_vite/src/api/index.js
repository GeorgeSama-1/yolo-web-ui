/**
 * API Module - Encapsulates all backend API calls
 */

const API_BASE = ''

/**
 * Fetch wrapper with error handling
 */
async function fetchAPI(url, options = {}) {
  const response = await fetch(url, options)
  const data = await response.json()

  if (!response.ok) {
    throw new Error(data.error || 'Request failed')
  }

  return data
}

/**
 * Get all available models
 */
export async function getModels() {
  return fetchAPI(`${API_BASE}/api/models`)
}

/**
 * Get current model classes
 */
export async function getClasses() {
  return fetchAPI(`${API_BASE}/api/classes`)
}

/**
 * Switch to a different model
 */
export async function switchModel(modelKey) {
  return fetchAPI(`${API_BASE}/api/switch_model`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ model_key: modelKey })
  })
}

/**
 * Re-detect the current image with temporary thresholds
 */
export async function redetectImage(imagePath, confidenceThreshold, iouThreshold) {
  return fetchAPI(`${API_BASE}/api/redetect`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      image_path: imagePath,
      confidence_threshold: confidenceThreshold,
      iou_threshold: iouThreshold
    })
  })
}

/**
 * Upload an image for detection
 */
export async function uploadImage(file, originalPath) {
  const formData = new FormData()
  formData.append('image', file)
  if (originalPath) {
    formData.append('original_path', originalPath)
  }

  return fetchAPI(`${API_BASE}/api/upload`, {
    method: 'POST',
    body: formData
  })
}

/**
 * Export single detection result as LabelMe JSON
 */
export async function exportLabelMe(exportPayload) {
  return fetchAPI(`${API_BASE}/api/export_labelme`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(exportPayload)
  })
}

/**
 * Batch export multiple detection results as ZIP
 */
export async function batchExportLabelMe(items) {
  return fetchAPI(`${API_BASE}/api/batch_export_labelme`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ items })
  })
}

/**
 * Delete a single image and its annotations
 */
export async function deleteImage(imagePath) {
  return fetchAPI(`${API_BASE}/api/delete_image`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ image_path: imagePath })
  })
}

/**
 * Batch delete multiple images
 */
export async function batchDeleteImages(imagePaths) {
  return fetchAPI(`${API_BASE}/api/batch_delete_images`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ image_paths: imagePaths })
  })
}

/**
 * Delete a single detection box from an image
 */
export async function deleteDetection(imagePath, detectionId) {
  return fetchAPI(`${API_BASE}/api/delete_detection`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ image_path: imagePath, detection_id: detectionId })
  })
}

/**
 * Clear all uploaded images and exported outputs
 */
export async function clearAllUploads() {
  return fetchAPI(`${API_BASE}/api/clear_all_uploads`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' }
  })
}

/**
 * Download a file (triggers browser download)
 */
export function downloadFile(url, filename) {
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

/**
 * Reload full image from backend by path (for on-demand loading)
 */
export async function reloadImage(imagePath) {
  return fetchAPI(`${API_BASE}/api/reload_image`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ image_path: imagePath })
  })
}
