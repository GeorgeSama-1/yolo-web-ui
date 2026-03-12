<template>
  <MainLayout @open-settings="openSettingsPanel">
    <!-- Left Panel Slot -->
    <template #left-panel>
      <SidebarHistory
        @delete-selected="handleDeleteSelectedHistory"
        @open-comparison="openComparisonPanel"
      />
    </template>

    <!-- Center Panel Slot -->
    <template #center-panel>
      <CanvasViewer
        ref="canvasViewerRef"
        :image-base64="displayImageBase64"
        :current-image-name="currentImageName"
        :mark-status="currentMarkStatus"
        :insulator-count="currentInsulatorCount"
        :avg-confidence="currentAvgConfidence"
        :detections="currentDetections"
        :selected-detection-boxes="selectedDetectionBoxes"
        :hovered-detection-id="hoveredDetectionId"
        @upload-click="triggerFileUpload"
        @mark-pass="handleMarkPass"
        @mark-fail="handleMarkFail"
        @stats-update="handleStatsUpdate"
        @detection-click="handleDetectionClick"
        @detection-hover="handleDetectionHover"
        @delete-selected-detections="handleDeleteSelectedDetections"
        @clear-all-history="handleClearAllHistory"
        @model-changed="handleModelChange"
      />
    </template>

    <!-- Right Panel Slot -->
    <template #right-panel>
      <SidebarControls
        ref="controlsRef"
        :current-image-path="currentImagePath"
        :current-detections="currentDetections"
        :current-image-item="currentImageItem"
        :status-value="currentStatusValue"
        :detection-count="currentInsulatorCount"
        :avg-confidence="currentAvgConfidence"
        :is-batch-processing="isBatchProcessing"
        :processed-count="processedCount"
        :total-files-to-process="totalFilesToProcess"
        @upload-files="handleUploadFiles"
        @export-current="handleExportCurrent"
        @batch-export="handleBatchExport"
        @stop-processing="handleStopProcessing"
      />
    </template>
  </MainLayout>

  <!-- Toast Notification -->
  <Toast
    :show="toast.show"
    :type="toast.type"
    :title="toast.title"
    :message="toast.message"
    :duration="toast.duration"
    :progress-current="toast.progressCurrent"
    :progress-total="toast.progressTotal"
    @close="toast.show = false"
  />
</template>

<script setup>
import { ref, computed, onMounted, watch, reactive } from 'vue'
import MainLayout from '@/layouts/MainLayout.vue'
import SidebarHistory from '@/components/SidebarHistory.vue'
import CanvasViewer from '@/components/CanvasViewer.vue'
import SidebarControls from '@/components/SidebarControls.vue'
import Toast from '@/components/shared/Toast.vue'
import { useDetectionState } from '@/composables/useDetectionState'
import * as api from '@/api'

// State management
const state = useDetectionState()

// Refs
const canvasViewerRef = ref(null)
const controlsRef = ref(null)
const fileInputRef = ref(null)
const folderInputRef = ref(null)

// Local state
const displayImageBase64 = ref(null)
const currentAvgConfidence = ref('-')
const currentInsulatorCount = ref('-')
const currentStatusValue = ref('-')
const userSelectedHistory = ref(false) // Track if user manually selected a history item
const isReloadingImage = ref(false) // Track image reload state

// Toast state
const toast = reactive({
  show: false,
  type: 'info',
  title: '',
  message: '',
  duration: 3000,
  progressCurrent: undefined,
  progressTotal: undefined
})

// Show toast notification
function showToast(type, title, message = '', duration = 3000, progressCurrent = undefined, progressTotal = undefined) {
  toast.type = type
  toast.title = title
  toast.message = message
  toast.duration = duration
  toast.progressCurrent = progressCurrent
  toast.progressTotal = progressTotal
  toast.show = true
}

// Update toast progress (for batch processing)
function updateToastProgress(current, total) {
  toast.progressCurrent = current
  toast.progressTotal = total
}

// Computed from state
const {
  history,
  currentImage,
  currentDetections,
  currentImagePath,
  currentImageName,
  currentImageItem,
  currentMarkStatus,
  availableModels,
  currentModelKey,
  pendingFiles,
  processedFiles,
  selectedHistoryItems,
  selectedFileItems,
  isBatchProcessing,
  processedCount,
  totalFilesToProcess,
  selectedDetectionBoxes,
  hoveredDetectionId,
  addToHistory,
  loadFromHistory,
  markCurrent,
  clearCurrentDisplay,
  setModels,
  setCurrentModel,
  getCurrentModel,
  setModelClasses,
  addPendingFiles,
  updateFileStatus,
  moveToProcessed,
  clearFiles,
  startBatchProcessing,
  stopBatchProcessing,
  endBatchProcessing,
  incrementProcessedCount,
  deleteMultipleHistoryItems,
  toggleDetectionBoxSelection,
  selectAllDetections,
  clearDetectionSelection,
  setHoveredDetection,
  deleteSelectedDetections,
  updateCurrentDetections
} = state

// Hidden file inputs
function createHiddenInputs() {
  const fileInput = document.createElement('input')
  fileInput.type = 'file'
  fileInput.accept = 'image/*'
  fileInput.multiple = true
  fileInput.style.display = 'none'
  fileInput.onchange = (e) => handleUploadFiles(Array.from(e.target.files))
  document.body.appendChild(fileInput)
  fileInputRef.value = fileInput

  const folderInput = document.createElement('input')
  folderInput.type = 'file'
  folderInput.accept = 'image/*'
  folderInput.webkitdirectory = true
  folderInput.directory = true
  folderInput.style.display = 'none'
  folderInput.onchange = (e) => handleUploadFiles(Array.from(e.target.files))
  document.body.appendChild(folderInput)
  folderInputRef.value = folderInput
}

function triggerFileUpload() {
  fileInputRef.value?.click()
}

// Track the latest processed image id during batch processing
const latestProcessedId = ref(null)

// Watch for current image item changes to update display
watch(currentImageItem, async (newItem, oldItem) => {
  if (newItem) {
    // Check if this is a user manual selection during batch processing
    if (isBatchProcessing.value && newItem.id !== latestProcessedId.value) {
      userSelectedHistory.value = true
    }

    // Reload full image on demand if not cached
    if (!newItem.imageBase64 && newItem.path && !isBatchProcessing.value) {
      await reloadFullImage(newItem)
    }

    // Always update display when currentImageItem changes
    // The userSelectedHistory flag prevents unwanted updates in handleUploadFiles
    displayImageBase64.value = newItem.imageBase64
    currentInsulatorCount.value = newItem.count !== undefined ? newItem.count : '-'

    if (!isBatchProcessing.value) {
      currentStatusValue.value = '检测完成'
    }

    if (newItem.detections && newItem.detections.length > 0) {
      currentAvgConfidence.value = (newItem.detections.reduce((sum, d) => sum + d.confidence, 0) / newItem.detections.length).toFixed(3)
    } else {
      currentAvgConfidence.value = '-'
    }

    // Clean up old item's imageBase64 to save memory (keep last 5 items in memory)
    if (oldItem && oldItem.id !== newItem.id) {
      const oldIndex = history.value.findIndex(h => h.id === oldItem.id)
      if (oldIndex > 4) { // Keep recent items in cache
        oldItem.imageBase64 = null
      }
    }
  } else {
    displayImageBase64.value = null
    currentInsulatorCount.value = '-'
    currentAvgConfidence.value = '-'
    currentStatusValue.value = '-'
  }
}, { immediate: true })

// Watch for batch processing status to update status value
watch([isBatchProcessing, processedCount, totalFilesToProcess], ([isProcessing, processed, total]) => {
  if (isProcessing) {
    // Reset user selection flag when batch processing starts
    if (processed === 0) {
      userSelectedHistory.value = false
    }
    // Update toast progress if showing loading toast
    if (toast.show && toast.type === 'loading') {
      updateToastProgress(processed, total)
    }
  } else {
    // Batch processing ended
    userSelectedHistory.value = false
  }
})

/**
 * Reload full image from backend on demand
 * Caches the result in the history item
 */
async function reloadFullImage(historyItem) {
  if (!historyItem.path || isReloadingImage.value) {
    return
  }

  try {
    isReloadingImage.value = true
    currentStatusValue.value = '加载中...'

    const result = await api.reloadImage(historyItem.path)

    if (result.success && result.image_base64) {
      // Cache the full image in the history item
      historyItem.imageBase64 = result.image_base64
    } else {
      console.warn('Failed to reload image:', result.error)
      // Fall back to thumbnail if reload fails
      historyItem.imageBase64 = historyItem.thumbnailBase64
    }
  } catch (error) {
    console.error('Reload image error:', error)
    // Fall back to thumbnail
    historyItem.imageBase64 = historyItem.thumbnailBase64
  } finally {
    isReloadingImage.value = false
  }
}

// Load models on mount
onMounted(async () => {
  createHiddenInputs()
  try {
    const data = await api.getModels()
    setModels(data.models, data.current_model)

    // Load class information for the current model
    try {
      const classesData = await api.getClasses()
      if (classesData.success && classesData.classes) {
        setModelClasses(classesData.classes)
        console.log('✅ Loaded class information:', classesData.classes)
        console.log('✅ Number of classes:', Object.keys(classesData.classes).length)
      } else {
        console.warn('⚠️ No class information in response')
      }
    } catch (error) {
      console.warn('⚠️ Failed to load class information:', error)
      // Continue without class info - will use defaults
    }
  } catch (error) {
    console.error('Failed to load models:', error)
    alert('无法加载模型列表')
  }
})

// Handle file upload
async function handleUploadFiles(files) {
  const imageFiles = files.filter(f => f.type.startsWith('image/'))

  if (imageFiles.length === 0) {
    showToast('error', '上传失败', '请选择图片文件！')
    return
  }

  // Show loading toast with progress
  const totalFiles = imageFiles.length
  showToast('loading', '批量检测中', '正在处理图片...', 0, 0, totalFiles)

  // Start batch processing
  startBatchProcessing(totalFiles)

  // Add to pending files
  addPendingFiles(imageFiles)

  // Process each file sequentially
  for (const file of imageFiles) {
    if (state.shouldStopProcessing.value) {
      // Clear remaining pending files
      state.pendingFiles.value = []
      break
    }

    const fileItem = state.pendingFiles.value.find(f => f.file.name === file.name)
    if (!fileItem) continue

    // Update status to processing
    updateFileStatus(fileItem, 'processing')

    try {
      // Upload and detect
      const result = await api.uploadImage(file, file.webkitRelativePath || file.name)

      if (result.success) {
        console.log('✅ Detection result received:', result)
        console.log('  Detections count:', result.detections?.length || 0)
        if (result.detections && result.detections.length > 0) {
          console.log('  First detection:', result.detections[0])
        }

        // Update file item status
        fileItem.result = result
        updateFileStatus(fileItem, 'completed')

        // Move to processed
        moveToProcessed(fileItem)

        // Add to history
        addToHistory(result)

        // Track the latest processed id for user selection detection
        latestProcessedId.value = result.image_id

        // Only update display if user hasn't manually selected another history item
        if (!userSelectedHistory.value) {
          // Load from history to properly update currentImageItem
          console.log('📋 Loading from history (index 0)')
          loadFromHistory(0) // New items are added at the beginning (index 0)
          console.log('  After loadFromHistory - currentDetections:', currentDetections.value?.length || 0)
        }
      } else {
        updateFileStatus(fileItem, 'error')
      }
    } catch (error) {
      console.error('Detection error:', error)
      updateFileStatus(fileItem, 'error')
    }

    incrementProcessedCount()
  }

  endBatchProcessing()

  // Close loading toast and show success message
  const finalProcessedCount = processedCount.value
  if (toast.show && toast.type === 'loading') {
    toast.show = false
  }
  showToast('success', '批量检测完成', `成功处理 ${finalProcessedCount} 张图片`)
}

// Handle model change
async function handleModelChange(modelKey) {
  if (!modelKey || modelKey === currentModelKey.value) {
    canvasViewerRef.value?.setModelSwitching(false)
    return
  }

  try {
    const data = await api.switchModel(modelKey)
    if (data.success) {
      setCurrentModel(modelKey)
      showToast('success', '模型切换成功', `当前使用: ${data.model_name}`)

      // Reload class information for the new model
      try {
        const classesData = await api.getClasses()
        if (classesData.success && classesData.classes) {
          setModelClasses(classesData.classes)
          console.log('Updated class information:', classesData.classes)
        }
      } catch (error) {
        console.warn('Failed to update class information:', error)
      }
    } else {
      showToast('error', '切换模型失败', data.error)
    }
  } catch (error) {
    console.error('Switch model error:', error)
    showToast('error', '切换模型失败', error.message)
  } finally {
    canvasViewerRef.value?.setModelSwitching(false)
  }
}

// Handle export current
async function handleExportCurrent() {
  if (!currentImagePath.value || !currentDetections.value.length) {
    alert('没有可导出的数据！')
    return
  }

  try {
    const result = await api.exportLabelMe(
      currentImagePath.value,
      currentDetections.value,
      currentImageItem.value?.modelInfo
    )

    if (result.success) {
      api.downloadFile(result.download_url, result.json_path)
      alert(`导出成功: ${result.json_path}`)
    } else {
      alert('导出失败: ' + result.error)
    }
  } catch (error) {
    console.error('Export error:', error)
    alert('导出失败: ' + error.message)
  }
}

// Handle batch export
async function handleBatchExport() {
  const selectedItems = []

  // Collect history selections
  selectedHistoryItems.value.forEach(index => {
    const item = history.value[index]
    selectedItems.push({
      image_path: item.path,
      detections: item.detections,
      image_name: item.imageName,
      model_info: item.modelInfo
    })
  })

  // Collect file list selections
  selectedFileItems.value.forEach(index => {
    const item = processedFiles.value[index]
    if (item.result) {
      selectedItems.push({
        image_path: item.result.image_path,
        detections: item.result.detections,
        image_name: item.file.name
      })
    }
  })

  if (selectedItems.length === 0) {
    alert('请先选择要导出的项目！')
    return
  }

  try {
    const result = await api.batchExportLabelMe(selectedItems)

    if (result.success) {
      api.downloadFile(result.download_url, result.filename)
      alert(`批量导出成功！已导出 ${selectedItems.length} 个文件`)
    } else {
      alert('批量导出失败: ' + result.error)
    }
  } catch (error) {
    console.error('Batch export error:', error)
    alert('批量导出失败: ' + error.message)
  }
}

// Handle delete selected history
async function handleDeleteSelectedHistory(indices) {
  try {
    // Get paths to delete
    const pathsToDelete = indices.map(idx => history.value[idx].path)

    // Call API
    const result = await api.batchDeleteImages(pathsToDelete)

    if (result.success) {
      // Delete from state
      const { deletedPaths, deletedIds } = deleteMultipleHistoryItems(indices)

      // Clear current display if deleted
      if (currentImagePath.value && deletedPaths.includes(currentImagePath.value)) {
        clearCurrentDisplay()
        displayImageBase64.value = null
      }

      alert(`成功删除 ${indices.length} 条记录`)
    } else {
      alert('删除失败: ' + result.error)
    }
  } catch (error) {
    console.error('Delete error:', error)
    alert('删除失败: ' + error.message)
  }
}

// Handle clear all history
function handleClearAllHistory() {
  // Clear all history from state
  const { clearHistory } = state
  clearHistory()

  // Clear current display
  clearCurrentDisplay()
  displayImageBase64.value = null

  // Clear selections
  selectedDetectionBoxes.value.clear()
  selectedHistoryItems.value.clear()
}

// Handle mark pass/fail
function handleMarkPass() {
  markCurrent('pass')
}

function handleMarkFail() {
  markCurrent('fail')
}

// Handle stop processing
function handleStopProcessing() {
  stopBatchProcessing()
}

// Handle stats update from canvas viewer
function handleStatsUpdate(stats) {
  currentAvgConfidence.value = stats.avgConfidence
  currentInsulatorCount.value = stats.detectionCount
}

// Handle detection box click
function handleDetectionClick(detectionId) {
  toggleDetectionBoxSelection(detectionId)
}

// Handle detection box hover
function handleDetectionHover(detectionId) {
  setHoveredDetection(detectionId)
}

// Handle delete selected detections
async function handleDeleteSelectedDetections() {
  if (selectedDetectionBoxes.value.size === 0) {
    alert('请先选择要删除的检测框！')
    return
  }

  if (!confirm(`确定要删除选中的 ${selectedDetectionBoxes.value.size} 个检测框吗？`)) {
    return
  }

  // Delete from local state first
  const deletedCount = deleteSelectedDetections()

  // Update statistics
  if (currentImageItem.value && currentImageItem.value.detections) {
    const newDetections = currentImageItem.value.detections
    if (newDetections.length > 0) {
      currentAvgConfidence.value = (newDetections.reduce((sum, d) => sum + d.confidence, 0) / newDetections.length).toFixed(3)
    } else {
      currentAvgConfidence.value = '-'
    }
    currentInsulatorCount.value = newDetections.length
  }

  alert(`已删除 ${deletedCount} 个检测框`)
}

// Open comparison panel
function openComparisonPanel() {
  // Get selected history items
  const selectedItems = []
  selectedHistoryItems.value.forEach(index => {
    const item = history.value[index]
    if (item) {
      selectedItems.push(item)
    }
  })

  if (selectedItems.length < 2) {
    alert('请先在左侧历史记录中选中至少2张图片进行对比！\n\n使用复选框选择要对比的图片，然后点击"模型对比"按钮。')
    return
  }

  if (selectedItems.length > 4) {
    alert('最多只能同时对比4张图片！')
    return
  }

  // Create comparison panel
  const panel = window.open('', '_blank', 'width=1400,height=900')
  panel.document.write(`
    <!DOCTYPE html>
    <html>
    <head>
      <title>模型对比</title>
      <style>
        * { box-sizing: border-box; }
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #1a1a2e; min-height: 100vh; }
        h1 { color: #fff; text-align: center; padding: 10px 0 20px; margin: 0; }
        .comparison-grid {
          display: grid;
          grid-template-columns: repeat(${Math.min(selectedItems.length, 2)}, 1fr);
          gap: 20px;
          max-width: 1400px;
          margin: 0 auto;
        }
        .comparison-item {
          background: #16213e;
          border-radius: 12px;
          overflow: hidden;
          box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        }
        .item-header {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          padding: 15px 20px;
          color: white;
        }
        .model-name { font-size: 18px; font-weight: bold; margin-bottom: 5px; }
        .image-name { font-size: 13px; opacity: 0.9; }
        .item-stats {
          display: flex;
          justify-content: space-around;
          padding: 15px;
          background: #0f3460;
          color: #fff;
        }
        .stat { text-align: center; }
        .stat-value { font-size: 28px; font-weight: bold; color: #e94560; }
        .stat-label { font-size: 12px; color: #aaa; margin-top: 3px; }
        .item-image {
          width: 100%;
          aspect-ratio: 4/3;
          object-fit: contain;
          background: #000;
          display: block;
        }
        .item-detections {
          padding: 15px;
          max-height: 150px;
          overflow-y: auto;
          background: #1a1a2e;
        }
        .detection-item {
          display: flex;
          justify-content: space-between;
          padding: 8px 12px;
          margin: 5px 0;
          background: #16213e;
          border-radius: 6px;
          color: #fff;
          font-size: 13px;
        }
        .detection-conf { color: #4ade80; font-weight: 600; }
      </style>
    </head>
    <body>
      <h1>📊 模型检测结果对比 (${selectedItems.length} 张图片)</h1>
      <div class="comparison-grid">
        ${selectedItems.map(item => {
          const avgConf = item.detections && item.detections.length > 0
            ? (item.detections.reduce((sum, d) => sum + d.confidence, 0) / item.detections.length).toFixed(3)
            : '-'
          return `
            <div class="comparison-item">
              <div class="item-header">
                <div class="model-name">${item.modelInfo ? item.modelInfo.name : '未知模型'}</div>
                <div class="image-name">📷 ${item.imageName}</div>
              </div>
              <div class="item-stats">
                <div class="stat">
                  <div class="stat-value">${item.count}</div>
                  <div class="stat-label">检测数量</div>
                </div>
                <div class="stat">
                  <div class="stat-value">${avgConf}</div>
                  <div class="stat-label">平均置信度</div>
                </div>
                <div class="stat">
                  <div class="stat-value">${item.detections ? item.detections.length : 0}</div>
                  <div class="stat-label">检测框数</div>
                </div>
              </div>
              <img class="item-image" src="data:image/jpeg;base64,${item.imageBase64}" alt="${item.imageName}">
              ${item.detections && item.detections.length > 0 ? `
                <div class="item-detections">
                  ${item.detections.slice(0, 10).map((d, i) => `
                    <div class="detection-item">
                      <span>检测 #${i + 1}</span>
                      <span class="detection-conf">${(d.confidence * 100).toFixed(1)}%</span>
                    </div>
                  `).join('')}
                  ${item.detections.length > 10 ? `<div class="detection-item"><span>... 还有 ${item.detections.length - 10} 个检测框</span></div>` : ''}
                </div>
              ` : ''}
            </div>
          `
        }).join('')}
      </div>
    </body>
    </html>
  `)
  panel.document.close()
}

function openSettingsPanel() {
  if (canvasViewerRef.value) {
    canvasViewerRef.value.showBoxSettings()
  }
}
</script>
