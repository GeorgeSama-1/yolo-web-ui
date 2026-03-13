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
        <button
          v-if="hasImage"
          data-testid="add-detection-button"
          @click="addDetection"
          class="px-4 py-2 bg-amber-500 text-white rounded-lg cursor-pointer text-sm transition-all hover:bg-amber-600"
        >
          + 补加框
        </button>
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

    <div
      v-if="selectedDetectionForEditing"
      class="px-4 py-3 border-b border-amber-200 bg-amber-50 flex items-center justify-between gap-4 flex-shrink-0"
    >
      <div>
        <div class="text-sm font-semibold text-amber-900">实例校正</div>
        <div class="text-xs text-amber-700 mt-1">
          当前选中检测框 #{{ selectedDetectionForEditing.id }}，可直接修改类别标签。
        </div>
      </div>
      <div class="min-w-48">
        <label class="block text-xs font-medium text-amber-800 mb-1">类别标签</label>
        <select
          data-testid="detection-class-select"
          :value="String(selectedDetectionForEditing.class_id ?? 0)"
          class="w-full rounded-lg border border-amber-300 bg-white px-3 py-2 text-sm text-gray-800 outline-none focus:border-amber-400 focus:ring-2 focus:ring-amber-200"
          @change="handleDetectionClassChange($event.target.value)"
        >
          <option
            v-for="item in editableClassOptions"
            :key="item.classId"
            :value="String(item.classId)"
          >
            {{ item.className }}
          </option>
        </select>
      </div>
      <div class="min-w-40">
        <label class="block text-xs font-medium text-amber-800 mb-1">框宽度</label>
        <input
          data-testid="detection-width-input"
          type="range"
          min="20"
          :max="Math.max(canvasWidth || 400, 20)"
          :value="selectedDetectionWidth"
          class="w-full"
          @input="handleDetectionWidthChange($event.target.value)"
        >
      </div>
      <div class="min-w-40">
        <label class="block text-xs font-medium text-amber-800 mb-1">框高度</label>
        <input
          data-testid="detection-height-input"
          type="range"
          min="20"
          :max="Math.max(canvasHeight || 300, 20)"
          :value="selectedDetectionHeight"
          class="w-full"
          @input="handleDetectionHeightChange($event.target.value)"
        >
      </div>
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
        <div
          v-if="selectedDetectionForEditing"
          class="absolute rounded border-2 border-emerald-400 pointer-events-none"
          :style="selectedDetectionOverlayStyle"
        >
          <button
            v-for="handle in resizeHandles"
            :key="handle.key"
            type="button"
            class="absolute h-3 w-3 rounded-full border border-white bg-emerald-500 shadow-sm pointer-events-auto"
            :class="handle.cursor"
            :style="handle.style"
            @mousedown.stop="startResizeDetection(handle.key, $event)"
          ></button>
        </div>
      </div>
    </div>

    <!-- Box Settings Panel -->
    <div
      v-if="showBoxSettingsPanel"
      data-testid="settings-panel"
      class="absolute top-20 right-4 bg-white rounded-lg shadow-xl border border-gray-200 p-4 z-50 w-72 max-h-[calc(100vh-7rem)] overflow-y-auto"
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

      <!-- Box Style Section -->
      <div class="mb-4">
        <h4 class="text-sm font-semibold text-gray-700 mb-3">🎨 检测框样式</h4>
        <p class="mb-4 rounded-lg border border-blue-200 bg-blue-50 px-3 py-2 text-xs leading-relaxed text-blue-700">
          检测框颜色会跟随类别自动变化，这里只调整边框宽度和标签字号。
        </p>

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
import { createCenteredBBox, moveBBox, resizeBBoxFromHandle } from '@/utils/detectionEditing'
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

const emit = defineEmits(['upload-click', 'mark-pass', 'mark-fail', 'stats-update', 'detection-click', 'detection-hover', 'delete-selected-detections', 'update-detection-class', 'add-detection', 'update-detection-bbox'])

// Refs
const canvasRef = ref(null)
const wrapperRef = ref(null)
const containerRef = ref(null)

// State
const zoom = ref(1)
const panX = ref(0)
const panY = ref(0)
const isDragging = ref(false)
const isDraggingDetection = ref(false)
const isResizingDetection = ref(false)
const dragStartX = ref(0)
const dragStartY = ref(0)
const dragDetectionStart = ref(null)
const resizeHandle = ref(null)
const originalImage = ref(null)
const hasImage = ref(false)
const isHoveringBox = ref(false)
const canvasWidth = ref(0)
const canvasHeight = ref(0)

// Box settings state
const showBoxSettingsPanel = ref(false)

// Destructure box style state from global state
const {
  boxStrokeColor,
  boxFillColor,
  boxLineWidth,
  boxFontSize,
  setBoxLineWidth,
  setBoxFontSize,
  getClassColor,
  getClassName,
  modelClasses
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

const editableClassOptions = computed(() => {
  const classes = modelClasses.value
  if (!classes || Object.keys(classes).length === 0) {
    return [{ classId: 0, className: 'class_0' }]
  }

  return Object.entries(classes)
    .map(([classId, className]) => ({
      classId: Number(classId),
      className
    }))
    .sort((left, right) => left.classId - right.classId)
})

const selectedDetectionForEditing = computed(() => {
  if (!props.detections || props.selectedDetectionBoxes?.size !== 1) {
    return null
  }

  const [selectedId] = Array.from(props.selectedDetectionBoxes)
  return props.detections.find(detection => detection.id === selectedId) || null
})

const selectedDetectionWidth = computed(() => {
  if (!selectedDetectionForEditing.value) return 0
  const [x1, , x2] = selectedDetectionForEditing.value.bbox
  return Math.max(x2 - x1, 0)
})

const selectedDetectionHeight = computed(() => {
  if (!selectedDetectionForEditing.value) return 0
  const [, y1, , y2] = selectedDetectionForEditing.value.bbox
  return Math.max(y2 - y1, 0)
})

const selectedDetectionOverlayStyle = computed(() => {
  if (!selectedDetectionForEditing.value) return {}
  const [x1, y1, x2, y2] = selectedDetectionForEditing.value.bbox
  return {
    left: `${x1}px`,
    top: `${y1}px`,
    width: `${Math.max(x2 - x1, 0)}px`,
    height: `${Math.max(y2 - y1, 0)}px`
  }
})

const resizeHandles = computed(() => ([
  { key: 'nw', cursor: 'cursor-nwse-resize', style: { left: '-6px', top: '-6px' } },
  { key: 'ne', cursor: 'cursor-nesw-resize', style: { right: '-6px', top: '-6px' } },
  { key: 'sw', cursor: 'cursor-nesw-resize', style: { left: '-6px', bottom: '-6px' } },
  { key: 'se', cursor: 'cursor-nwse-resize', style: { right: '-6px', bottom: '-6px' } }
]))

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

function resetBoxStyles() {
  // 只重置线宽和字号，颜色由类别自动确定
  setBoxLineWidth(2)
  setBoxFontSize(12)
}

function handleDetectionClassChange(nextClassId) {
  if (!selectedDetectionForEditing.value) {
    return
  }

  const classId = Number(nextClassId)
  const classOption = editableClassOptions.value.find(item => item.classId === classId)

  emit('update-detection-class', {
    detectionId: selectedDetectionForEditing.value.id,
    classId,
    className: classOption?.className || `class_${classId}`
  })
}

function addDetection() {
  emit('add-detection', {
    bbox: createCenteredBBox(canvasWidth.value || 400, canvasHeight.value || 300)
  })
}

function getCanvasCoordinates(event) {
  if (!canvasRef.value) {
    return null
  }

  const rect = canvasRef.value.getBoundingClientRect()
  const scaleX = canvasWidth.value / rect.width
  const scaleY = canvasHeight.value / rect.height

  return {
    x: (event.clientX - rect.left) * scaleX,
    y: (event.clientY - rect.top) * scaleY
  }
}

function emitDetectionBBoxUpdate(bbox) {
  if (!selectedDetectionForEditing.value) {
    return
  }

  emit('update-detection-bbox', {
    detectionId: selectedDetectionForEditing.value.id,
    bbox
  })
}

function handleDetectionWidthChange(nextWidth) {
  if (!selectedDetectionForEditing.value) {
    return
  }

  const width = Math.max(Number(nextWidth), 20)
  const [x1, y1, , y2] = selectedDetectionForEditing.value.bbox
  emitDetectionBBoxUpdate([x1, y1, x1 + width, y2])
}

function handleDetectionHeightChange(nextHeight) {
  if (!selectedDetectionForEditing.value) {
    return
  }

  const height = Math.max(Number(nextHeight), 20)
  const [x1, y1, x2] = selectedDetectionForEditing.value.bbox
  emitDetectionBBoxUpdate([x1, y1, x2, y1 + height])
}

function startResizeDetection(handle, event) {
  if (!selectedDetectionForEditing.value) {
    return
  }

  const point = getCanvasCoordinates(event)
  if (!point) {
    return
  }

  isResizingDetection.value = true
  resizeHandle.value = handle
  dragDetectionStart.value = {
    point,
    bbox: [...selectedDetectionForEditing.value.bbox]
  }
}

function handleMouseDown(e) {
  if (!hasImage.value) return

  const point = getCanvasCoordinates(e)
  if (point && selectedDetectionForEditing.value) {
    const selectedId = findBoxAtPosition(point.x, point.y)
    if (selectedId === selectedDetectionForEditing.value.id) {
      isDraggingDetection.value = true
      dragDetectionStart.value = {
        point,
        bbox: [...selectedDetectionForEditing.value.bbox]
      }
      return
    }
  }

  if (isHoveringBox.value) return
  isDragging.value = true
  dragStartX.value = e.clientX - panX.value
  dragStartY.value = e.clientY - panY.value
}

function handleMouseMove(e) {
  if (!hasImage.value) return

  if (isResizingDetection.value && dragDetectionStart.value && resizeHandle.value) {
    const point = getCanvasCoordinates(e)
    if (!point) {
      return
    }

    emitDetectionBBoxUpdate(
      resizeBBoxFromHandle({
        bbox: dragDetectionStart.value.bbox,
        handle: resizeHandle.value,
        deltaX: point.x - dragDetectionStart.value.point.x,
        deltaY: point.y - dragDetectionStart.value.point.y,
        canvasWidth: canvasWidth.value,
        canvasHeight: canvasHeight.value
      })
    )
    return
  }

  if (isDraggingDetection.value && dragDetectionStart.value) {
    const point = getCanvasCoordinates(e)
    if (!point) {
      return
    }

    emitDetectionBBoxUpdate(
      moveBBox(
        dragDetectionStart.value.bbox,
        point.x - dragDetectionStart.value.point.x,
        point.y - dragDetectionStart.value.point.y,
        canvasWidth.value,
        canvasHeight.value
      )
    )
    return
  }

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
  isDraggingDetection.value = false
  isResizingDetection.value = false
  dragDetectionStart.value = null
  resizeHandle.value = null
}

function handleMouseLeave() {
  isDragging.value = false
  isDraggingDetection.value = false
  isResizingDetection.value = false
  dragDetectionStart.value = null
  resizeHandle.value = null
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
  hasImage,
  canvasWidth,
  canvasHeight
})
</script>
