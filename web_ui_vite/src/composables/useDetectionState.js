/**
 * Global State Management Composable
 * Manages all application state for detection workflow
 */

import { ref, computed, watch } from 'vue'
import { MAX_HISTORY, MARK_STATUS, FILE_STATUS } from '@/utils/constants'

// Global state (shared across all components using this composable)
const state = {
  history: ref([]),
  currentImage: ref(null),
  currentDetections: ref([]),
  currentImagePath: ref(null),
  currentImageName: ref(null),
  currentImageItem: ref(null),
  selectedHistoryItems: ref(new Set()),
  selectedFileItems: ref(new Set()),
  historyStatus: ref({}), // { image_id: 'pass' | 'fail' | 'none' }
  folderExpandedState: ref({}), // { folder_name: true | false }
  availableModels: ref([]),
  currentModelKey: ref(null),
  pendingFiles: ref([]),
  processedFiles: ref([]),
  isBatchProcessing: ref(false),
  shouldStopProcessing: ref(false),
  totalFilesToProcess: ref(0),
  processedCount: ref(0),
  // Filter state
  modelFilter: ref('all'),
  enableCountFilter: ref(false),
  countThreshold: ref(70),
  // Detection box state
  selectedDetectionBoxes: ref(new Set()),
  hoveredDetectionId: ref(null),
  canvasScale: ref(1),
  canvasOffsetX: ref(0),
  canvasOffsetY: ref(0),
  // Detection box style settings
  boxStrokeColor: ref('#ef4444'),
  boxFillColor: ref('rgba(239, 68, 68, 0.2)'),
  boxLineWidth: ref(2),
  boxFontSize: ref(12),
  // Multi-class support
  modelClasses: ref({}), // { class_id: class_name }
  classColorMap: ref({}), // { class_id: color }
  classColorMapHistory: ref([]) // 保存所有模型的类别颜色映射历史
}

/**
 * Use Detection State Composable
 * Returns reactive state and actions for managing detection workflow
 */
export function useDetectionState() {
  // ==================== Computed Properties ====================

  const filteredHistory = computed(() => {
    let filtered = state.history.value

    // Model filter
    if (state.modelFilter.value !== 'all') {
      filtered = filtered.filter(item => {
        return item.modelInfo && item.modelInfo.key === state.modelFilter.value
      })
    }

    // Count filter
    if (state.enableCountFilter.value) {
      const threshold = state.countThreshold.value || 70
      filtered = filtered.filter(item => item.count < threshold)
    }

    return filtered
  })

  const selectedCount = computed(() => {
    return state.selectedHistoryItems.value.size + state.selectedFileItems.value.size
  })

  const currentMarkStatus = computed(() => {
    if (!state.currentImageItem.value) return MARK_STATUS.NONE
    return state.historyStatus.value[state.currentImageItem.value.id] || MARK_STATUS.NONE
  })

  // ==================== History Actions ====================

  function addToHistory(result) {
    // Extract folder info from original path
    const originalPath = result.original_path || result.image_name
    const pathParts = originalPath.split(/[\/\\]/)

    let folderName = 'root'
    let displayName = originalPath

    if (pathParts.length > 1) {
      folderName = pathParts.slice(0, -1).join('-')
      displayName = pathParts[pathParts.length - 1]
    }

    // Add model prefix to folder name to distinguish different model results
    const modelInfo = result.model_info || null
    if (modelInfo && modelInfo.name) {
      folderName = `[${modelInfo.name}] ${folderName}`
    }

    const historyItem = {
      id: result.image_id,
      // Only store thumbnail, not full image to save memory
      // thumbnailBase64: result.thumbnail_base64,
      imageBase64: null, // Don't store full image
      thumbnailBase64: result.thumbnail_base64 || result.image_base64?.substring(0, 5000), // Use thumbnail or truncated preview
      imageName: displayName,
      fullName: originalPath,
      count: result.insulator_count,
      path: result.image_path,
      detections: result.detections,
      timestamp: new Date().toLocaleTimeString(),
      folderName: folderName,
      modelInfo: modelInfo
    }

    // Add to beginning
    state.history.value.unshift(historyItem)

    // Limit history and cleanup memory
    if (state.history.value.length > MAX_HISTORY) {
      const removed = state.history.value.pop()
      delete state.historyStatus.value[removed.id]
      if (removed.imageBase64) removed.imageBase64 = null
      if (removed.thumbnailBase64) removed.thumbnailBase64 = null
    }
  }

  function deleteHistoryItem(index) {
    const item = state.history.value[index]
    if (!item) return null

    // Remove from history
    state.history.value.splice(index, 1)

    // Clean up status
    delete state.historyStatus.value[item.id]

    // Update selection indices
    updateSelectionIndices(state.selectedHistoryItems, index)
    updateSelectionIndices(state.selectedFileItems, index)

    return item
  }

  function deleteMultipleHistoryItems(indices) {
    const sortedIndices = [...indices].sort((a, b) => b - a)
    const deletedItems = []
    const deletedPaths = []
    const deletedIds = []

    sortedIndices.forEach(index => {
      const item = state.history.value[index]
      if (item) {
        deletedItems.push(item)
        if (item.path) deletedPaths.push(item.path)
        if (item.id) deletedIds.push(item.id)
        state.history.value.splice(index, 1)
        delete state.historyStatus.value[item.id]
      }
    })

    // Update selection indices
    updateSelectionIndicesAfterMultipleDelete(state.selectedHistoryItems, sortedIndices)
    updateSelectionIndicesAfterMultipleDelete(state.selectedFileItems, sortedIndices)

    return { deletedItems, deletedPaths, deletedIds }
  }

  function loadFromHistory(index) {
    const item = state.history.value[index]
    if (!item) {
      return null
    }

    state.currentImageItem.value = item
    state.currentDetections.value = item.detections
    state.currentImagePath.value = item.path
    state.currentImageName.value = item.fullName || item.imageName

    return item
  }

  function clearHistory() {
    state.history.value = []
    state.historyStatus.value = {}
    state.selectedHistoryItems.value.clear()
  }

  // ==================== Selection Actions ====================

  function toggleHistorySelection(index) {
    if (state.selectedHistoryItems.value.has(index)) {
      state.selectedHistoryItems.value.delete(index)
    } else {
      state.selectedHistoryItems.value.add(index)
    }
  }

  function toggleFileSelection(index) {
    if (state.selectedFileItems.value.has(index)) {
      state.selectedFileItems.value.delete(index)
    } else {
      state.selectedFileItems.value.add(index)
    }
  }

  function selectAllHistory() {
    state.history.value.forEach((_, index) => {
      state.selectedHistoryItems.value.add(index)
    })
  }

  function clearAllHistorySelection() {
    state.selectedHistoryItems.value.clear()
  }

  function selectAllFiles() {
    state.processedFiles.value.forEach((_, index) => {
      state.selectedFileItems.value.add(index)
    })
  }

  function clearAllFilesSelection() {
    state.selectedFileItems.value.clear()
  }

  // ==================== Mark Actions ====================

  function markItem(itemId, status) {
    // Use spread to ensure reactivity trigger
    state.historyStatus.value = {
      ...state.historyStatus.value,
      [itemId]: status
    }
  }

  function markCurrent(status) {
    if (!state.currentImageItem.value) return false
    const itemId = state.currentImageItem.value.id
    // Use spread to ensure reactivity trigger
    state.historyStatus.value = {
      ...state.historyStatus.value,
      [itemId]: status
    }
    return true
  }

  function clearAllMarks() {
    state.historyStatus.value = {}
  }

  // ==================== Folder Actions ====================

  function toggleFolder(folderName) {
    const current = state.folderExpandedState.value[folderName]
    state.folderExpandedState.value[folderName] = current === false ? true : false
  }

  // ==================== Model Actions ====================

  function setModels(models, currentModelKey) {
    state.availableModels.value = models
    state.currentModelKey.value = currentModelKey
  }

  function setCurrentModel(modelKey) {
    state.currentModelKey.value = modelKey
  }

  function getCurrentModel() {
    return state.availableModels.value.find(m => m.key === state.currentModelKey.value)
  }

  // ==================== Class & Color Actions ====================

  function setModelClasses(classes) {
    console.log('🔄 Setting model classes:', classes)
    state.modelClasses.value = classes
    // 为新类别生成颜色映射
    generateClassColorMap(classes)
    console.log('✅ Model classes and color map updated')
  }

  function generateClassColorMap(classes) {
    const colorMap = {}
    const classIds = Object.keys(classes).map(Number)

    console.log('🎨 Generating class color map for classes:', classes)
    console.log('🎨 Class IDs:', classIds)

    // 为每个类别分配颜色
    // 二分类：abnormal(0)用红色，normal(1)用绿色
    const predefinedColors = [
      { stroke: '#ef4444', fill: 'rgba(239, 68, 68, 0.2)' },  // 红色 - abnormal (有问题)
      { stroke: '#22c55e', fill: 'rgba(34, 197, 94, 0.2)' },  // 绿色 - normal (正常)
      { stroke: '#f59e0b', fill: 'rgba(245, 158, 11, 0.2)' },  // 橙色 - 第三类别
      { stroke: '#3b82f6', fill: 'rgba(59, 130, 246, 0.2)' }, // 蓝色
      { stroke: '#8b5cf6', fill: 'rgba(139, 92, 246, 0.2)' }, // 紫色
      { stroke: '#ec4899', fill: 'rgba(236, 72, 153, 0.2)' }, // 粉色
      { stroke: '#06b6d4', fill: 'rgba(6, 182, 212, 0.2)' },  // 青色
      { stroke: '#84cc16', fill: 'rgba(132, 204, 22, 0.2)' },  // 黄绿色
      { stroke: '#f97316', fill: 'rgba(249, 115, 22, 0.2)' },  // 深橙色
      { stroke: '#6366f1', fill: 'rgba(99, 102, 241, 0.2)' }  // 靛蓝色
    ]

    classIds.forEach((classId, index) => {
      if (index < predefinedColors.length) {
        colorMap[classId] = predefinedColors[index]
        console.log(`  ✓ Class ${classId}: ${classes[classId]} -> ${predefinedColors[index].stroke}`)
      } else {
        // 如果类别超过预定义颜色，生成随机颜色
        const hue = (index * 137.508) % 360 // 使用黄金角度分布
        colorMap[classId] = {
          stroke: `hsl(${hue}, 70%, 50%)`,
          fill: `hsla(${hue}, 70%, 50%, 0.2)`
        }
        console.log(`  ✨ Class ${classId}: ${classes[classId]} -> generated color (hue: ${hue})`)
      }
    })

    state.classColorMap.value = colorMap
    console.log('🎨 Final color map:', colorMap)

    // 保存到历史记录
    state.classColorMapHistory.value.push({
      modelKey: state.currentModelKey.value,
      classes: { ...classes },
      colorMap: { ...colorMap },
      timestamp: Date.now()
    })

    // 更新默认框颜色为第一个类别的颜色
    if (classIds.length > 0) {
      const firstClassColor = colorMap[classIds[0]]
      state.boxStrokeColor.value = firstClassColor.stroke
      state.boxFillColor.value = firstClassColor.fill
      console.log('🎨 Updated default box color to:', firstClassColor.stroke)
    }
  }

  function getClassColor(classId) {
    console.log(`🔍 getClassColor called: classId=${classId}`)
    console.log(`  Available classColorMap:`, state.classColorMap.value)

    const color = state.classColorMap.value[classId]
    if (color) {
      console.log(`  ✓ Found color for class ${classId}:`, color)
      return color
    }

    // 如果没有找到类别特定的颜色，使用默认颜色
    console.warn(`⚠️ No color found for class ${classId}, using default color: ${state.boxStrokeColor.value}`)
    return {
      stroke: state.boxStrokeColor.value,
      fill: state.boxFillColor.value
    }
  }

  function getClassName(classId) {
    const className = state.modelClasses.value[classId] || `class_${classId}`
    console.log(`🏷️ getClassName: classId=${classId} -> className=${className}`)
    console.log(`  Available modelClasses:`, state.modelClasses.value)
    return className
  }

  function getClassIdByName(className) {
    const entries = Object.entries(state.modelClasses.value)
    for (const [id, name] of entries) {
      if (name === className) return Number(id)
    }
    return null
  }

  // ==================== File Processing Actions ====================

  function addPendingFiles(files) {
    files.forEach(file => {
      if (!state.pendingFiles.value.find(f => f.file.name === file.name)) {
        state.pendingFiles.value.push({
          file,
          status: FILE_STATUS.PENDING,
          result: null
        })
      }
    })
  }

  function updateFileStatus(fileItem, status, result = null) {
    fileItem.status = status
    if (result) {
      fileItem.result = result
    }
  }

  function moveToProcessed(fileItem) {
    const index = state.pendingFiles.value.indexOf(fileItem)
    if (index !== -1) {
      state.pendingFiles.value.splice(index, 1)
      state.processedFiles.value.push(fileItem)
    }
  }

  function clearFiles() {
    state.pendingFiles.value = []
    state.processedFiles.value = []
    state.selectedFileItems.value.clear()
  }

  function startBatchProcessing(totalFiles) {
    state.isBatchProcessing.value = true
    state.shouldStopProcessing.value = false
    state.totalFilesToProcess.value = totalFiles
    state.processedCount.value = 0
  }

  function stopBatchProcessing() {
    state.shouldStopProcessing.value = true
  }

  function endBatchProcessing() {
    state.isBatchProcessing.value = false
  }

  function incrementProcessedCount() {
    state.processedCount.value++
  }

  // ==================== Filter Actions ====================

  function setFilters(filters) {
    if (filters.modelFilter !== undefined) state.modelFilter.value = filters.modelFilter
    if (filters.enableCountFilter !== undefined) state.enableCountFilter.value = filters.enableCountFilter
    if (filters.countThreshold !== undefined) state.countThreshold.value = filters.countThreshold
  }

  // ==================== Helper Functions ====================

  function updateSelectionIndices(selectionSet, deletedIndex) {
    const newSelection = new Set()
    selectionSet.forEach(idx => {
      if (idx < deletedIndex) {
        newSelection.add(idx)
      } else if (idx > deletedIndex) {
        newSelection.add(idx - 1)
      }
    })
    selectionSet.clear()
    newSelection.forEach(idx => selectionSet.add(idx))
  }

  function updateSelectionIndicesAfterMultipleDelete(selectionSet, deletedIndices) {
    const newSelection = new Set()
    let newIndex = 0

    for (let i = 0; i < state.history.value.length + deletedIndices.length; i++) {
      if (!deletedIndices.includes(i) && selectionSet.has(i)) {
        newSelection.add(newIndex)
      }
      if (!deletedIndices.includes(i)) {
        newIndex++
      }
    }

    selectionSet.clear()
    newSelection.forEach(idx => selectionSet.add(idx))
  }

  // ==================== Detection Box Actions ====================

  function selectDetectionBox(detectionId) {
    state.selectedDetectionBoxes.value.add(detectionId)
  }

  function deselectDetectionBox(detectionId) {
    state.selectedDetectionBoxes.value.delete(detectionId)
  }

  function toggleDetectionBoxSelection(detectionId) {
    if (state.selectedDetectionBoxes.value.has(detectionId)) {
      state.selectedDetectionBoxes.value.delete(detectionId)
    } else {
      state.selectedDetectionBoxes.value.add(detectionId)
    }
  }

  function selectAllDetections() {
    if (state.currentDetections.value) {
      state.currentDetections.value.forEach(d => {
        state.selectedDetectionBoxes.value.add(d.id)
      })
    }
  }

  function clearDetectionSelection() {
    state.selectedDetectionBoxes.value.clear()
  }

  function setHoveredDetection(detectionId) {
    state.hoveredDetectionId.value = detectionId
  }

  function setCanvasTransform(scale, offsetX, offsetY) {
    state.canvasScale.value = scale
    state.canvasOffsetX.value = offsetX
    state.canvasOffsetY.value = offsetY
  }

  function updateCurrentDetections(newDetections) {
    state.currentDetections.value = newDetections
    // Update currentImageItem as well
    if (state.currentImageItem.value) {
      state.currentImageItem.value.detections = newDetections
    }
  }

  function deleteSelectedDetections() {
    if (!state.currentDetections.value) return 0

    const selectedIds = Array.from(state.selectedDetectionBoxes.value)
    const filteredDetections = state.currentDetections.value.filter(
      d => !selectedIds.includes(d.id)
    )

    // Re-number the remaining detections
    filteredDetections.forEach((d, index) => {
      d.id = index + 1
    })

    state.currentDetections.value = filteredDetections

    // Update currentImageItem
    if (state.currentImageItem.value) {
      state.currentImageItem.value.detections = filteredDetections
      state.currentImageItem.value.count = filteredDetections.length
    }

    // Clear selection
    state.selectedDetectionBoxes.value.clear()

    return selectedIds.length
  }

  // ==================== Box Style Actions ====================

  function setBoxStrokeColor(color) {
    state.boxStrokeColor.value = color
  }

  function setBoxFillColor(color) {
    state.boxFillColor.value = color
  }

  function setBoxLineWidth(width) {
    state.boxLineWidth.value = width
  }

  function setBoxFontSize(size) {
    state.boxFontSize.value = size
  }

  // ==================== Clear Current Display ====================

  function clearCurrentDisplay() {
    state.currentImage.value = null
    state.currentDetections.value = []
    state.currentImagePath.value = null
    state.currentImageName.value = null
    state.currentImageItem.value = null
    state.selectedDetectionBoxes.value.clear()
    state.hoveredDetectionId.value = null
  }

  // ==================== Return State and Actions ====================

  return {
    // State
    history: state.history,
    currentImage: state.currentImage,
    currentDetections: state.currentDetections,
    currentImagePath: state.currentImagePath,
    currentImageName: state.currentImageName,
    currentImageItem: state.currentImageItem,
    selectedHistoryItems: state.selectedHistoryItems,
    selectedFileItems: state.selectedFileItems,
    historyStatus: state.historyStatus,
    folderExpandedState: state.folderExpandedState,
    availableModels: state.availableModels,
    currentModelKey: state.currentModelKey,
    pendingFiles: state.pendingFiles,
    processedFiles: state.processedFiles,
    isBatchProcessing: state.isBatchProcessing,
    shouldStopProcessing: state.shouldStopProcessing,
    totalFilesToProcess: state.totalFilesToProcess,
    processedCount: state.processedCount,
    modelFilter: state.modelFilter,
    enableCountFilter: state.enableCountFilter,
    countThreshold: state.countThreshold,
    // Detection box state
    selectedDetectionBoxes: state.selectedDetectionBoxes,
    hoveredDetectionId: state.hoveredDetectionId,
    canvasScale: state.canvasScale,
    canvasOffsetX: state.canvasOffsetX,
    canvasOffsetY: state.canvasOffsetY,
    // Detection box style settings
    boxStrokeColor: state.boxStrokeColor,
    boxFillColor: state.boxFillColor,
    boxLineWidth: state.boxLineWidth,
    boxFontSize: state.boxFontSize,
    // Multi-class state
    modelClasses: state.modelClasses,
    classColorMap: state.classColorMap,
    classColorMapHistory: state.classColorMapHistory,
    // Computed
    filteredHistory,
    selectedCount,
    currentMarkStatus,
    // Actions
    addToHistory,
    deleteHistoryItem,
    deleteMultipleHistoryItems,
    loadFromHistory,
    clearHistory,
    toggleHistorySelection,
    toggleFileSelection,
    selectAllHistory,
    clearAllHistorySelection,
    selectAllFiles,
    clearAllFilesSelection,
    markItem,
    markCurrent,
    clearAllMarks,
    toggleFolder,
    setModels,
    setCurrentModel,
    getCurrentModel,
    // Class & color actions
    setModelClasses,
    generateClassColorMap,
    getClassColor,
    getClassName,
    getClassIdByName,
    addPendingFiles,
    updateFileStatus,
    moveToProcessed,
    clearFiles,
    startBatchProcessing,
    stopBatchProcessing,
    endBatchProcessing,
    incrementProcessedCount,
    setFilters,
    selectDetectionBox,
    deselectDetectionBox,
    toggleDetectionBoxSelection,
    selectAllDetections,
    clearDetectionSelection,
    setHoveredDetection,
    setCanvasTransform,
    updateCurrentDetections,
    deleteSelectedDetections,
    clearCurrentDisplay,
    // Box style actions
    setBoxStrokeColor,
    setBoxFillColor,
    setBoxLineWidth,
    setBoxFontSize
  }
}
