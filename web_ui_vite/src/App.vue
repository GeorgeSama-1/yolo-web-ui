<template>
  <MainLayout @open-settings="openSettingsPanel">
    <!-- Left Panel Slot -->
    <template #left-panel>
      <SidebarHistory
        @delete-selected="handleDeleteSelectedHistory"
        @open-comparison="openComparisonPanel"
        @clear-history="handleClearHistoryOnly"
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
        :two-stage-enabled="currentTwoStageEnabled"
        :normal-count="currentNormalCount"
        :abnormal-count="currentAbnormalCount"
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
        @update-detection-class="handleUpdateDetectionClass"
        @add-detection="handleAddDetection"
        @update-detection-bbox="handleUpdateDetectionBBox"
      />
    </template>

    <!-- Right Panel Slot -->
    <template #right-panel>
      <SidebarControls
        ref="controlsRef"
        :current-image-path="currentImagePath"
        :current-image-name="currentImageName"
        :current-detections="currentDetections"
        :classification-model-name="classificationModelName"
        :classification-model-path="classificationModelPath"
        :status-value="currentStatusValue"
        :detection-count="currentInsulatorCount"
        :normal-count="currentNormalCount"
        :abnormal-count="currentAbnormalCount"
        :two-stage-enabled="currentTwoStageEnabled"
        :avg-confidence="currentAvgConfidence"
        :is-batch-processing="isBatchProcessing"
        :processed-count="processedCount"
        :total-files-to-process="totalFilesToProcess"
        :is-redetecting="isRedetecting"
        :is-model-switching="isModelSwitching"
        @upload-files="handleUploadFiles"
        @model-changed="handleModelChange"
        @redetect-current="handleRedetectCurrent"
        @export-current="handleExportCurrent"
        @batch-export="handleBatchExport"
        @stop-processing="handleStopProcessing"
        @clear-all-uploads="handleClearAllUploads"
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
import {
  buildComparisonHtml,
  buildExportAnnotationPayload,
  deleteSelectedDetectionsOnServer,
  prepareComparisonItems
} from '@/utils/appHelpers'

// State management
const state = useDetectionState()

// Refs
const canvasViewerRef = ref(null)
const fileInputRef = ref(null)
const folderInputRef = ref(null)

// Local state
const displayImageBase64 = ref(null)
const currentAvgConfidence = ref('-')
const currentInsulatorCount = ref('-')
const currentStatusValue = ref('-')
const currentNormalCount = ref(0)
const currentAbnormalCount = ref(0)
const currentTwoStageEnabled = ref(false)
const classificationModelName = ref('')
const classificationModelPath = ref('')
const userSelectedHistory = ref(false) // Track if user manually selected a history item
const isReloadingImage = ref(false) // Track image reload state
const isRedetecting = ref(false)
const isModelSwitching = ref(false)

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
  selectAllDetections,
  clearDetectionSelection,
  setHoveredDetection,
  deleteSelectedDetections,
  updateCurrentDetections,
  updateDetectionClass,
  addDetectionBox
  ,
  updateDetectionBBox
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
    currentNormalCount.value = newItem.normalCount ?? 0
    currentAbnormalCount.value = newItem.abnormalCount ?? 0
    currentTwoStageEnabled.value = newItem.twoStageEnabled ?? false

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
    currentNormalCount.value = 0
    currentAbnormalCount.value = 0
    currentTwoStageEnabled.value = false
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
      currentTwoStageEnabled.value = data.two_stage_enabled ?? false
      classificationModelName.value = data.classification_model?.name || ''
      classificationModelPath.value = data.classification_model?.path || ''

      // Load class information for the current model
      try {
        const classesData = await api.getClasses()
        if (classesData.success && classesData.classes) {
          setModelClasses(classesData.classes)
          currentTwoStageEnabled.value = classesData.two_stage_enabled ?? currentTwoStageEnabled.value
          classificationModelName.value = classesData.classification_model?.name || classificationModelName.value
          classificationModelPath.value = classesData.classification_model?.path || classificationModelPath.value
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

        if (result.model_info?.classes) {
          setModelClasses(result.model_info.classes)
        }
        currentTwoStageEnabled.value = result.two_stage_enabled ?? currentTwoStageEnabled.value
        classificationModelName.value = result.classification_model?.name || classificationModelName.value
        classificationModelPath.value = result.classification_model?.path || classificationModelPath.value

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
    return
  }

  try {
    isModelSwitching.value = true
    const data = await api.switchModel(modelKey)
    if (data.success) {
      setCurrentModel(modelKey)
      showToast('success', '模型切换成功', `当前使用: ${data.model_name}`)
      currentTwoStageEnabled.value = data.two_stage_enabled ?? currentTwoStageEnabled.value
      classificationModelName.value = data.classification_model?.name || classificationModelName.value
      classificationModelPath.value = data.classification_model?.path || classificationModelPath.value

      // Reload class information for the new model
      try {
        const classesData = await api.getClasses()
        if (classesData.success && classesData.classes) {
          setModelClasses(classesData.classes)
          currentTwoStageEnabled.value = classesData.two_stage_enabled ?? currentTwoStageEnabled.value
          classificationModelName.value = classesData.classification_model?.name || classificationModelName.value
          classificationModelPath.value = classesData.classification_model?.path || classificationModelPath.value
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
    isModelSwitching.value = false
  }
}

// Handle export current
async function handleExportCurrent() {
  if (!currentImagePath.value || !currentDetections.value.length) {
    alert('没有可导出的数据！')
    return
  }

  try {
    const exportPayload = buildExportAnnotationPayload({
      imagePath: currentImagePath.value,
      imageName: currentImageItem.value?.imageName,
      originalPath: currentImageItem.value?.fullName,
      detections: currentDetections.value,
      modelInfo: currentImageItem.value?.modelInfo
    })

    const result = await api.exportLabelMe(exportPayload)

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
        image_name: item.imageName,
        original_path: item.fullName,
        detections: item.detections,
        model_info: item.modelInfo
      })
  })

  // Collect file list selections
  selectedFileItems.value.forEach(index => {
    const item = processedFiles.value[index]
        if (item.result) {
          selectedItems.push({
            image_path: item.result.image_path,
            image_name: item.result.image_name,
            original_path: item.result.original_path,
            detections: item.result.detections,
            model_info: item.result.model_info
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
  clearFiles()

  // Clear current display
  clearCurrentDisplay()
  displayImageBase64.value = null

  // Clear selections
  selectedDetectionBoxes.value.clear()
  selectedHistoryItems.value.clear()
}

async function handleClearAllUploads() {
  if (!confirm('确定要清空所有上传的图片和导出的文件吗？此操作不可恢复！')) {
    return
  }

  try {
    const result = await api.clearAllUploads()

    if (!result.success) {
      showToast('error', '清空失败', result.error || '未知错误')
      return
    }

    handleClearAllHistory()
    showToast(
      'success',
      '清空成功',
      `已删除 ${result.upload_count ?? 0} 个上传文件和 ${result.output_count ?? 0} 个导出文件`
    )
  } catch (error) {
    console.error('Clear uploads error:', error)
    showToast('error', '清空失败', error.message)
  }
}

function handleClearHistoryOnly() {
  const { clearHistory } = state
  clearHistory()
  clearCurrentDisplay()
  displayImageBase64.value = null
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
  if (detectionId == null) {
    clearDetectionSelection()
    return
  }

  selectedDetectionBoxes.value = new Set([detectionId])
}

// Handle detection box hover
function handleDetectionHover(detectionId) {
  setHoveredDetection(detectionId)
}

function handleUpdateDetectionClass({ detectionId, classId, className }) {
  const updatedDetection = updateDetectionClass(detectionId, classId, className)
  if (!updatedDetection) {
    return
  }

  processedFiles.value.forEach(fileItem => {
    if (fileItem.result?.image_path !== currentImagePath.value || !fileItem.result?.detections) {
      return
    }

    fileItem.result.detections = fileItem.result.detections.map(detection => (
      detection.id === detectionId
        ? { ...detection, class_id: classId, class_name: className }
        : detection
    ))
  })

  showToast('success', '类别已更新', `检测框 #${detectionId} 已标记为 ${className}`, 1800)
}

function handleAddDetection({ bbox }) {
  const nextDetection = addDetectionBox({ bbox })
  if (!nextDetection) {
    return
  }

  processedFiles.value.forEach(fileItem => {
    if (fileItem.result?.image_path !== currentImagePath.value || !fileItem.result?.detections) {
      return
    }

    fileItem.result.detections = [...fileItem.result.detections, nextDetection]
  })

  showToast('success', '已补加检测框', `新增实例 #${nextDetection.id}`, 1800)
}

function handleUpdateDetectionBBox({ detectionId, bbox }) {
  const updatedDetection = updateDetectionBBox(detectionId, bbox)
  if (!updatedDetection) {
    return
  }

  processedFiles.value.forEach(fileItem => {
    if (fileItem.result?.image_path !== currentImagePath.value || !fileItem.result?.detections) {
      return
    }

    fileItem.result.detections = fileItem.result.detections.map(detection => (
      detection.id === detectionId
        ? { ...detection, bbox }
        : detection
    ))
  })
}

async function handleRedetectCurrent({ confidenceThreshold, iouThreshold }) {
  if (!currentImagePath.value || isRedetecting.value) {
    return
  }

  try {
    isRedetecting.value = true
    currentStatusValue.value = '重新检测中...'

    const result = await api.redetectImage(
      currentImagePath.value,
      confidenceThreshold,
      iouThreshold
    )

    if (result.model_info?.classes) {
      setModelClasses(result.model_info.classes)
    }
    classificationModelName.value = result.classification_model?.name || classificationModelName.value
    classificationModelPath.value = result.classification_model?.path || classificationModelPath.value

    updateCurrentDetections(result.detections || [])
    clearDetectionSelection()

    const totalCount = result.stage1_total_count ?? result.total_count ?? result.detections.length
    currentInsulatorCount.value = totalCount
    currentNormalCount.value = result.normal_count ?? 0
    currentAbnormalCount.value = result.abnormal_count ?? 0
    currentTwoStageEnabled.value = result.two_stage_enabled ?? false
    currentAvgConfidence.value = result.detections.length > 0
      ? (result.detections.reduce((sum, detection) => sum + detection.confidence, 0) / result.detections.length).toFixed(3)
      : '-'
    currentStatusValue.value = '重新检测完成'

    if (currentImageItem.value) {
      currentImageItem.value.detections = result.detections || []
      currentImageItem.value.count = totalCount
      currentImageItem.value.normalCount = result.normal_count ?? 0
      currentImageItem.value.abnormalCount = result.abnormal_count ?? 0
      currentImageItem.value.twoStageEnabled = result.two_stage_enabled ?? false
      if (result.class_counts) {
        currentImageItem.value.classCounts = result.class_counts
      }
      if (result.model_info) {
        currentImageItem.value.modelInfo = result.model_info
      }
    }

    processedFiles.value.forEach(fileItem => {
      if (fileItem.result?.image_path === currentImagePath.value) {
        fileItem.result = {
          ...fileItem.result,
          detections: result.detections || [],
          total_count: totalCount,
          insulator_count: totalCount,
          stage1_total_count: totalCount,
          normal_count: result.normal_count ?? 0,
          abnormal_count: result.abnormal_count ?? 0,
          two_stage_enabled: result.two_stage_enabled ?? false,
          class_counts: result.class_counts || {},
          model_info: result.model_info || fileItem.result.model_info
        }
      }
    })

    showToast(
      'success',
      '重新检测完成',
      `confidence=${confidenceThreshold.toFixed(2)}, IoU=${iouThreshold.toFixed(2)}`
    )
  } catch (error) {
    console.error('Redetect error:', error)
    currentStatusValue.value = '重新检测失败'
    showToast('error', '重新检测失败', error.message)
  } finally {
    isRedetecting.value = false
  }
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

  if (!currentImagePath.value) {
    alert('当前图片没有可删除的检测数据！')
    return
  }

  try {
    const result = await deleteSelectedDetectionsOnServer({
      imagePath: currentImagePath.value,
      detections: currentDetections.value,
      selectedIds: selectedDetectionBoxes.value,
      deleteDetection: api.deleteDetection
    })

    updateCurrentDetections(result.detections)
    if (currentImageItem.value) {
      currentImageItem.value.count = result.detections.length
    }
    selectedDetectionBoxes.value.clear()

    if (result.detections.length > 0) {
      currentAvgConfidence.value = (result.detections.reduce((sum, d) => sum + d.confidence, 0) / result.detections.length).toFixed(3)
    } else {
      currentAvgConfidence.value = '-'
    }
    currentInsulatorCount.value = result.detections.length

    alert(`已删除 ${result.deletedCount} 个检测框`)
  } catch (error) {
    console.error('Delete detections error:', error)
    alert(`删除检测框失败: ${error.message}`)
  }
}

// Open comparison panel
async function openComparisonPanel() {
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

  const preparedItems = await prepareComparisonItems(selectedItems, api.reloadImage)

  // Create comparison panel
  const panel = window.open('', '_blank', 'width=1400,height=900')
  if (!panel) {
    showToast('error', '打开失败', '浏览器拦截了对比窗口，请允许弹窗后重试。')
    return
  }
  panel.document.write(buildComparisonHtml(preparedItems))
  panel.document.close()
}

function openSettingsPanel() {
  if (canvasViewerRef.value) {
    canvasViewerRef.value.showBoxSettings()
  }
}
</script>
