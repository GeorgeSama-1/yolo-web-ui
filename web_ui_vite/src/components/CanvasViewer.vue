<template>
  <section class="flex-1 min-w-0 bg-white flex flex-col relative overflow-hidden">
    <!-- Toolbar -->
    <div class="flex items-center justify-between gap-2.5 px-3 py-2 bg-white border-b border-gray-200 flex-shrink-0">
      <div class="flex items-center gap-2.5">
        <button
          @click="zoomIn"
          class="px-4 py-2 bg-white border border-gray-300 rounded-lg cursor-pointer text-sm transition-all hover:bg-blue-50 hover:border-primary"
        >
          🔍+ 放大
        </button>
        <button
          @click="zoomOut"
          class="px-4 py-2 bg-white border border-gray-300 rounded-lg cursor-pointer text-sm transition-all hover:bg-blue-50 hover:border-primary"
        >
          🔍- 缩小
        </button>
        <button
          @click="fitToWindow"
          class="px-4 py-2 bg-white border border-gray-300 rounded-lg cursor-pointer text-sm transition-all hover:bg-blue-50 hover:border-primary"
        >
          ⊙ 适应窗口
        </button>
        <button
          @click="actualSize"
          class="px-4 py-2 bg-white border-gray-300 rounded-lg cursor-pointer text-sm transition-all hover:bg-blue-50 hover:border-primary"
        >
          1:1 实际尺寸
        </button>
        <div class="px-4 py-2 bg-gray-50 rounded-lg text-sm text-gray-600 min-w-20 text-center">
          {{ zoomPercent }}
        </div>
      </div>

      <div
        class="px-4 py-2 bg-gradient-to-r from-primary to-secondary text-white rounded-lg text-sm font-semibold overflow-hidden text-ellipsis whitespace-nowrap max-w-md"
      >
        {{ currentImageName || '未选择图片' }}
      </div>
    </div>

    <!-- Detection Info -->
    <div v-if="hasImage" class="px-4 py-2 bg-blue-50 border-b border-blue-200 flex items-center justify-between flex-shrink-0">
      <div class="flex items-center gap-4 text-sm">
        <span class="text-gray-600">检测框: <span class="font-semibold text-blue-600">{{ detectionCount }}</span> 个</span>
        <span class="text-gray-600">已选中: <span class="font-semibold text-green-600">{{ selectedCount }}</span> 个</span>
        <!-- Class breakdown -->
        <div v-if="classBreakdown.length > 0" class="flex items-center gap-2">
          <span class="text-gray-600">类别:</span>
          <span
            v-for="item in classBreakdown"
            :key="item.classId"
            class="px-2 py-0.5 rounded text-xs font-semibold text-white"
            :style="{ backgroundColor: item.color }"
          >
            {{ item.className }}: {{ item.count }}
          </span>
        </div>
      </div>
      <button
        v-if="selectedCount > 0"
        @click="$emit('delete-selected-detections')"
        class="px-3 py-1 bg-red-500 text-white rounded text-sm hover:bg-red-600 transition-colors"
      >
        删除选中 ({{ selectedCount }})
      </button>
    </div>

    <!-- Canvas Container -->
    <div
      ref="containerRef"
      class="flex-1 bg-white flex items-center justify-center relative overflow-hidden"
      :class="{ 'cursor-grab': hasImage && !isHoveringBox, 'cursor-grabbing': hasImage && isDragging, 'border-2 border-dashed border-gray-200': !hasImage }"
      @mousedown="handleMouseDown"
      @wheel.prevent="handleWheel"
      @mousemove="handleMouseMove"
      @mouseup="handleMouseUp"
      @mouseleave="handleMouseLeave"
    >
      <!-- Empty State -->
      <div
        v-if="!hasImage"
        class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-center z-5"
      >
        <button
          @click="$emit('upload-click')"
          class="px-10 py-5 text-lg bg-gradient-to-r from-primary to-secondary text-white border-none rounded-xl cursor-pointer shadow-lg transition-all hover:scale-105 hover:shadow-xl"
        >
          📁 上传图片开始检测
        </button>
      </div>

      <!-- Canvas Wrapper -->
      <div
        v-show="hasImage"
        ref="wrapperRef"
        class="relative rounded-lg shadow-lg"
        :style="wrapperStyle"
      >
        <canvas
          ref="canvasRef"
          class="block rounded-lg"
          @click="handleCanvasClick"
        ></canvas>
      </div>
    </div>

    <!-- Box Settings Panel -->
    <div
      v-if="showBoxSettingsPanel"
      class="absolute top-20 right-4 bg-white rounded-lg shadow-xl border border-gray-200 p-4 z-50 w-72"
    >
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-semibold text-gray-800">设置</h3>
        <button
          @click="hideBoxSettings"
          class="text-gray-400 hover:text-gray-600 text-xl leading-none"
        >
          ×
        </button>
      </div>

      <!-- Model Selection Section -->
      <div class="mb-4 pb-4 border-b border-gray-200">
        <h4 class="text-xs font-semibold text-gray-700 mb-2">🤖 检测模型</h4>

        <!-- Current Model Display -->
        <div>
          <label class="block text-xs font-medium text-gray-700 mb-1.5">选择模型</label>
          <select
            :value="currentModelKey"
            @change="handleModelChange($event.target.value)"
            :disabled="isModelSwitching"
            class="w-full px-2 py-1.5 border border-gray-300 rounded-lg text-xs focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
          >
            <option
              v-for="model in availableModels"
              :key="model.key"
              :value="model.key"
            >
              {{ model.name }} - {{ model.description }}
            </option>
          </select>
          <div v-if="isModelSwitching" class="text-xs text-blue-600 mt-1 flex items-center gap-1">
            <span class="inline-block animate-spin">⏳</span> 切换中...
          </div>
        </div>
      </div>

      <!-- Divider -->
      <div class="border-t border-gray-200 my-4"></div>

      <!-- Box Style Section -->
      <div class="mb-4 pb-4 border-b border-gray-200">
        <h4 class="text-sm font-semibold text-gray-700 mb-3">🎨 检测框样式</h4>

        <!-- Info text -->
        <div class="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
          <p class="text-xs text-blue-700">
            <span class="font-semibold">💡 提示：</span>
            检测框颜色由类别自动确定，每种类类使用固定颜色：
          </p>
          <div class="mt-2 space-y-1">
            <div class="flex items-center gap-2 text-xs text-blue-700">
              <span class="w-3 h-3 rounded-full" style="background-color: #ef4444;"></span>
              <span>异常</span>
            </div>
            <div class="flex items-center gap-2 text-xs text-blue-700">
              <span class="w-3 h-3 rounded-full" style="background-color: #22c55e;"></span>
              <span>正常</span>
            </div>
          </div>
        </div>

      <!-- Line Width -->
      <div class="mb-4">
        <label class="block text-sm font-medium text-gray-700 mb-2">
          边框宽度: <span class="font-semibold">{{ boxLineWidth }}px</span>
        </label>
        <input
          type="range"
          :value="boxLineWidth"
          @input="setBoxLineWidth(parseInt($event.target.value))"
          min="1"
          max="5"
          step="1"
          class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
        >
      </div>

      <!-- Font Size -->
      <div class="mb-4">
        <label class="block text-sm font-medium text-gray-700 mb-2">
          标签字号: <span class="font-semibold">{{ boxFontSize }}px</span>
        </label>
        <input
          type="range"
          :value="boxFontSize"
          @input="setBoxFontSize(parseInt($event.target.value))"
          min="10"
          max="20"
          step="1"
          class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
        >
      </div>
      </div>

      <!-- Divider -->
      <div class="border-t border-gray-200 my-4"></div>

      <!-- Clear Uploads Section -->
      <div class="mb-2">
        <h4 class="text-sm font-semibold text-gray-700 mb-2">数据管理</h4>
        <p class="text-xs text-gray-500 mb-3">清空所有上传的图片和导出的文件</p>
        <button
          @click="clearAllUploads"
          class="w-full px-3 py-2 text-sm bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
        >
          清空所有文件
        </button>
      </div>

      <!-- Divider -->
      <div class="border-t border-gray-200 my-4"></div>

      <!-- Buttons -->
      <div class="flex gap-2 mt-2">
        <button
          @click="resetBoxStyles"
          class="flex-1 px-3 py-2 text-sm bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
        >
          重置默认
        </button>
        <button
          @click="hideBoxSettings"
          class="flex-1 px-3 py-2 text-sm bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
        >
          完成
        </button>
      </div>
    </div>

    <!-- Bottom Actions (Mark Pass/Fail) -->
    <div
      v-if="hasImage"
      class="px-4 py-3 bg-white border-t border-gray-200 flex gap-3 justify-center shadow-sm z-20"
    >
      <button
        @click="$emit('mark-pass')"
        class="px-4 py-2 text-sm rounded-lg border-none cursor-pointer transition-all hover:-translate-y-0.5 hover:shadow-md"
        :class="markPassClass"
      >
        ✓ 标记为通过
      </button>
      <button
        @click="$emit('mark-fail')"
        class="px-4 py-2 text-sm rounded-lg border-none cursor-pointer transition-all hover:-translate-y-0.5 hover:shadow-md"
        :class="markFailClass"
      >
        ✗ 标记为未通过
      </button>
    </div>
  </section>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { calculateFitScale, clampZoom, formatZoomPercent } from '@/utils/canvas'
import { useDetectionState } from '@/composables/useDetectionState'

const state = useDetectionState()

const props = defineProps({
  imageBase64: {
    type: String,
    default: null
  },
  currentImageName: {
    type: String,
    default: null
  },
  markStatus: {
    type: String,
    default: 'none'
  },
  avgConfidence: {
    type: Number,
    default: null
  },
  insulatorCount: {
    type: Number,
    default: 0
  },
  detections: {
    type: Array,
    default: () => []
  },
  selectedDetectionBoxes: {
    type: Set,
    default: () => new Set()
  },
  hoveredDetectionId: {
    type: Number,
    default: null
  }
})

const emit = defineEmits(['upload-click', 'mark-pass', 'mark-fail', 'stats-update', 'detection-click', 'delete-selected-detections', 'clear-all-history', 'model-changed'])

// Refs
const canvasRef = ref(null)
const wrapperRef = ref(null)
const containerRef = ref(null)

// State
const zoom = ref(1)
const panX = ref(0)
const panY = ref(0)
const isDragging = ref(false)
const dragStartX = ref(0)
const dragStartY = ref(0)
const originalImage = ref(null)
const hasImage = ref(false)
const isHoveringBox = ref(false)
const canvasWidth = ref(0)
const canvasHeight = ref(0)

// Box settings state
const showBoxSettingsPanel = ref(false)
const isModelSwitching = ref(false)

// Destructure box style state from global state
const {
  boxStrokeColor,
  boxFillColor,
  boxLineWidth,
  boxFontSize,
  setBoxStrokeColor,
  setBoxFillColor,
  setBoxLineWidth,
  setBoxFontSize,
  availableModels,
  currentModelKey,
  setCurrentModel,
  getClassColor,
  getClassName
} = state

// Computed
const wrapperStyle = computed(() => ({
  transform: `translate(${panX.value}px, ${panY.value}px) scale(${zoom.value})`,
  transition: isDragging.value ? 'none' : 'transform 0.1s ease-out'
}))

const zoomPercent = computed(() => formatZoomPercent(zoom.value))

const detectionCount = computed(() => props.detections?.length || 0)

const selectedCount = computed(() => props.selectedDetectionBoxes?.size || 0)

const classBreakdown = computed(() => {
  if (!props.detections || props.detections.length === 0) return []

  const breakdown = {}
  props.detections.forEach(det => {
    const classId = det.class_id !== undefined ? det.class_id : 0
    const className = getClassName(classId)
    const classColor = getClassColor(classId)

    if (!breakdown[classId]) {
      breakdown[classId] = {
        classId,
        className,
        color: classColor.stroke,
        count: 0
      }
    }
    breakdown[classId].count++
  })

  return Object.values(breakdown).sort((a, b) => b.count - a.count)
})

const markPassClass = computed(() => {
  const isPass = props.markStatus === 'pass'
  return {
    'bg-gradient-to-r from-primary to-secondary text-white': isPass,
    'opacity-100': isPass,
    'opacity-60': !isPass
  }
})

const markFailClass = computed(() => {
  const isFail = props.markStatus === 'fail'
  return {
    'bg-red-500 text-white': isFail,
    'opacity-100': isFail,
    'opacity-60': !isFail,
    'hover:bg-red-600': isFail
  }
})

// Methods
function setZoom(newZoom) {
  zoom.value = clampZoom(newZoom)
}

function zoomIn() {
  setZoom(zoom.value * 1.2)
}

function zoomOut() {
  setZoom(zoom.value / 1.2)
}

function fitToWindow() {
  if (!containerRef.value || !originalImage.value) return

  const containerWidth = containerRef.value.clientWidth - 40
  const containerHeight = containerRef.value.clientHeight - 40

  const scale = calculateFitScale(
    containerWidth,
    containerHeight,
    originalImage.value.width,
    originalImage.value.height
  )

  setZoom(scale)
  panX.value = 0
  panY.value = 0
}

function actualSize() {
  setZoom(1)
  panX.value = 0
  panY.value = 0
}

function showBoxSettings() {
  showBoxSettingsPanel.value = true
}

function hideBoxSettings() {
  showBoxSettingsPanel.value = false
}

async function handleModelChange(modelKey) {
  if (isModelSwitching.value) return

  isModelSwitching.value = true

  // Emit event for parent to handle the actual switch
  emit('model-changed', modelKey)

  // Note: Parent component (App.vue) will call setModelSwitching(false)
  // after the API call completes via the setModelSwitching exposed method
}

function resetBoxStyles() {
  // 只重置线宽和字号，颜色由类别自动确定
  setBoxLineWidth(2)
  setBoxFontSize(12)
}

async function clearAllUploads() {
  if (!confirm('确定要清空所有上传的图片和导出的文件吗？此操作不可恢复！')) {
    return
  }

  try {
    const response = await fetch('/api/clear_all_uploads', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      }
    })

    const result = await response.json()

    if (result.success) {
      alert(`清空成功！已删除 ${result.upload_count} 个上传文件和 ${result.output_count} 个导出文件。`)
      // Emit event to clear history in parent component
      emit('clear-all-history')
    } else {
      alert(`清空失败: ${result.error}`)
    }
  } catch (error) {
    alert(`清空失败: ${error.message}`)
  }
}

function handleMouseDown(e) {
  if (!hasImage.value || isHoveringBox.value) return
  isDragging.value = true
  dragStartX.value = e.clientX - panX.value
  dragStartY.value = e.clientY - panY.value
}

function handleMouseMove(e) {
  if (!hasImage.value) return

  // Handle dragging
  if (isDragging.value) {
    panX.value = e.clientX - dragStartX.value
    panY.value = e.clientY - dragStartY.value
    return
  }

  // Handle box hover detection
  if (canvasRef.value) {
    const rect = canvasRef.value.getBoundingClientRect()
    const scaleX = canvasWidth.value / rect.width
    const scaleY = canvasHeight.value / rect.height
    const x = (e.clientX - rect.left) * scaleX
    const y = (e.clientY - rect.top) * scaleY

    const hoveredBox = findBoxAtPosition(x, y)

    if (hoveredBox !== null) {
      isHoveringBox.value = true
      emit('detection-hover', hoveredBox)
    } else {
      isHoveringBox.value = false
      emit('detection-hover', null)
    }
  }
}

function handleMouseUp() {
  isDragging.value = false
}

function handleMouseLeave() {
  isDragging.value = false
  isHoveringBox.value = false
  emit('detection-hover', null)
}

function handleWheel(e) {
  if (!hasImage.value) return
  const delta = e.deltaY > 0 ? 0.9 : 1.1
  setZoom(zoom.value * delta)
}

function handleCanvasClick(e) {
  if (!hasImage.value || !canvasRef.value) return

  const rect = canvasRef.value.getBoundingClientRect()
  const scaleX = canvasWidth.value / rect.width
  const scaleY = canvasHeight.value / rect.height
  const x = (e.clientX - rect.left) * scaleX
  const y = (e.clientY - rect.top) * scaleY

  const clickedBox = findBoxAtPosition(x, y)

  if (clickedBox !== null) {
    emit('detection-click', clickedBox)
  }
}

function findBoxAtPosition(x, y) {
  if (!props.detections) return null

  for (let i = props.detections.length - 1; i >= 0; i--) {
    const det = props.detections[i]
    const [x1, y1, x2, y2] = det.bbox

    if (x >= x1 && x <= x2 && y >= y1 && y <= y2) {
      return det.id
    }
  }

  return null
}

function loadImage(base64Data) {
  if (!base64Data) {
    hasImage.value = false
    if (canvasRef.value) {
      const ctx = canvasRef.value.getContext('2d')
      ctx.clearRect(0, 0, canvasRef.value.width, canvasRef.value.height)
      canvasRef.value.width = 0
      canvasRef.value.height = 0
    }
    originalImage.value = null
    return
  }

  const img = new Image()
  img.onload = () => {
    originalImage.value = img
    hasImage.value = true
    canvasWidth.value = img.width
    canvasHeight.value = img.height

    if (canvasRef.value) {
      canvasRef.value.width = img.width
      canvasRef.value.height = img.height
      render()
    }

    nextTick(() => {
      fitToWindow()
    })
  }

  img.src = `data:image/jpeg;base64,${base64Data}`
}

function render() {
  console.log('🖼️ render() called')
  console.log('  canvasRef:', canvasRef.value ? 'exists' : 'null')
  console.log('  originalImage:', originalImage.value ? 'exists' : 'null')
  console.log('  detections:', props.detections?.length || 0)

  if (!canvasRef.value || !originalImage.value) return

  const ctx = canvasRef.value.getContext('2d')

  // Clear and draw image
  ctx.clearRect(0, 0, canvasWidth.value, canvasHeight.value)
  ctx.drawImage(originalImage.value, 0, 0)

  // Draw detection boxes
  if (props.detections && props.detections.length > 0) {
    console.log('🎨 Drawing detection boxes, count:', props.detections.length)

    props.detections.forEach(det => {
      const [x1, y1, x2, y2] = det.bbox
      const isSelected = props.selectedDetectionBoxes?.has(det.id)
      const isHovered = props.hoveredDetectionId === det.id

      // Get class-specific color
      const classId = det.class_id !== undefined ? det.class_id : 0
      const classColor = getClassColor(classId)
      const className = getClassName(classId)

      console.log(`  📦 Box #${det.id}: classId=${classId}, className=${className}, color=${classColor.stroke}`)

      // Box style based on state - use custom styles or defaults
      if (isSelected) {
        // Selected: bright green with thicker border
        ctx.strokeStyle = '#22c55e'
        ctx.lineWidth = Math.max(boxLineWidth.value + 2, 3)
        ctx.fillStyle = 'rgba(34, 197, 94, 0.2)'
      } else if (isHovered) {
        // Hovered: bright yellow
        ctx.strokeStyle = '#eab308'
        ctx.lineWidth = Math.max(boxLineWidth.value + 1, 3)
        ctx.fillStyle = 'rgba(234, 179, 8, 0.15)'
      } else {
        // Default: use class-specific colors
        ctx.strokeStyle = classColor.stroke
        ctx.lineWidth = boxLineWidth.value
        ctx.fillStyle = classColor.fill
      }

      // Draw box
      ctx.fillRect(x1, y1, x2 - x1, y2 - y1)
      ctx.strokeRect(x1, y1, x2 - x1, y2 - y1)

      // Draw label background - include class name
      const labelText = `#${det.id} ${className} ${(det.confidence * 100).toFixed(0)}%`
      const fontSize = Math.max(boxFontSize.value, Math.floor(boxFontSize.value / zoom.value))
      ctx.font = `${fontSize}px Arial`
      const textWidth = ctx.measureText(labelText).width

      ctx.fillStyle = isSelected ? '#22c55e' : (isHovered ? '#eab308' : classColor.stroke)
      ctx.fillRect(x1, y1 - fontSize - 4, textWidth + 8, fontSize + 4)

      // Draw label text
      ctx.fillStyle = '#ffffff'
      ctx.fillText(labelText, x1 + 4, y1 - 6)
    })
  }

  // Emit stats update
  emit('stats-update', {
    avgConfidence: props.avgConfidence,
    detectionCount: props.detections?.length || 0
  })
}

// Watch for changes that require re-render
watch([
  () => props.imageBase64,
  () => props.detections,
  () => props.selectedDetectionBoxes,
  () => props.hoveredDetectionId,
  boxStrokeColor,
  boxFillColor,
  boxLineWidth,
  boxFontSize
], () => {
  render()
}, { deep: true })

// Watch for image changes
watch(() => props.imageBase64, (newBase64) => {
  loadImage(newBase64)
}, { immediate: true })

// Handle window resize
function handleResize() {
  if (hasImage.value) {
    fitToWindow()
  }
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})

// Expose methods for parent components
defineExpose({
  fitToWindow,
  actualSize,
  zoomIn,
  zoomOut,
  render,
  showBoxSettings,
  setModelSwitching: (value) => { isModelSwitching.value = value }
})
</script>
