<template>
  <div class="h-full flex flex-col">
    <!-- Current Model Display -->
    <div class="px-4 py-3 border-b border-cyan-500/20 bg-slate-800/30 flex-shrink-0">
      <div class="text-xs font-semibold text-cyan-400 mb-2 flex items-center gap-2">
        <span class="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse"></span>
        当前模型
      </div>
      <div class="px-3 py-2 bg-slate-900/50 rounded-lg border border-cyan-500/30">
        <div class="text-xs font-medium text-cyan-50 truncate" :title="currentModelName">
          {{ currentModelName }}
        </div>
        <div class="text-[10px] text-cyan-400/70 truncate mt-0.5" :title="currentModelDescription">
          {{ currentModelDescription }}
        </div>
      </div>
    </div>

    <!-- Class Information Display -->
    <div v-if="classList.length > 0" class="px-4 py-3 border-b border-cyan-500/20 bg-slate-800/30 flex-shrink-0">
      <div class="text-xs font-semibold text-cyan-400 mb-2 flex items-center gap-2">
        <span class="w-1.5 h-1.5 rounded-full bg-cyan-400"></span>
        检测类别 ({{ classList.length }})
      </div>
      <div class="grid grid-cols-2 gap-1.5">
        <div
          v-for="cls in classList"
          :key="cls.id"
          class="px-2 py-1.5 bg-slate-900/50 rounded border border-cyan-500/20 flex items-center gap-2"
        >
          <span
            class="w-3 h-3 rounded-full flex-shrink-0"
            :style="{ backgroundColor: cls.color }"
          ></span>
          <span class="text-[10px] text-cyan-50 truncate">{{ cls.name }}</span>
        </div>
      </div>
    </div>

    <!-- Upload Section -->
    <div class="px-4 py-3 border-b border-cyan-500/20 bg-slate-800/20 flex-shrink-0">
      <div class="flex gap-2 mb-2">
        <button
          @click="triggerFileInput"
          class="flex-1 px-3 py-2.5 text-sm bg-gradient-to-r from-cyan-500 to-blue-600 text-white rounded-lg transition-all hover:from-cyan-400 hover:to-blue-500 hover:shadow-lg hover:shadow-cyan-500/30 border border-cyan-400/30"
        >
          📄 选择文件
        </button>
        <button
          @click="triggerFolderInput"
          class="flex-1 px-3 py-2.5 text-sm bg-gradient-to-r from-cyan-500 to-blue-600 text-white rounded-lg transition-all hover:from-cyan-400 hover:to-blue-500 hover:shadow-lg hover:shadow-cyan-500/30 border border-cyan-400/30"
        >
          📁 文件夹
        </button>
      </div>
      <input
        ref="fileInputRef"
        type="file"
        accept="image/*"
        multiple
        class="hidden"
        @change="handleFileChange"
      >
      <input
        ref="folderInputRef"
        type="file"
        accept="image/*"
        webkitdirectory
        directory
        class="hidden"
        @change="handleFileChange"
      >
    </div>

    <!-- File List Section -->
    <div class="px-4 py-3 border-b border-cyan-500/20 bg-slate-800/30 flex-shrink-0">
      <div class="text-sm font-semibold text-cyan-400 mb-2 flex items-center gap-2">
        📋 文件列表
        <span class="text-xs text-cyan-400/60">(已选 {{ selectedFileItems.size }} 项)</span>
      </div>
      <div class="flex gap-2 mb-2">
        <button
          @click="selectAllFiles"
          class="flex-1 px-2 py-2 text-xs border border-cyan-500/30 rounded-lg bg-slate-700/50 text-cyan-400 hover:bg-slate-700 hover:border-cyan-500/50 transition-all"
        >
          全选
        </button>
        <button
          @click="clearAllFiles"
          class="flex-1 px-2 py-2 text-xs border border-cyan-500/30 rounded-lg bg-slate-700/50 text-cyan-400 hover:bg-slate-700 hover:border-cyan-500/50 transition-all"
        >
          清空
        </button>
      </div>
    </div>

    <!-- File List -->
    <div class="flex-1 overflow-y-auto px-4 py-2 min-h-0">
      <div v-if="pendingFiles.length === 0 && processedFiles.length === 0" class="px-5 py-5 text-center text-cyan-400/30 text-sm">
        暂无文件
      </div>

      <!-- Processed Files -->
      <FileItem
        v-for="(fileItem, index) in processedFiles"
        :key="fileItem.file.name"
        :file="fileItem.file"
        :status="fileItem.status"
        :result="fileItem.result"
        :show-checkbox="true"
        :is-selected="selectedFileItems.has(index)"
        @toggle-selection="toggleFileSelection(index)"
      />

      <!-- Pending Files -->
      <FileItem
        v-for="(fileItem, index) in pendingFiles"
        :key="fileItem.file.name"
        :file="fileItem.file"
        :status="fileItem.status"
        :result="fileItem.result"
        :show-checkbox="false"
      />
    </div>

    <!-- Statistics -->
    <div class="px-4 py-3 border-t border-cyan-500/20 bg-slate-800/30 flex-shrink-0">
      <div class="grid grid-cols-3 gap-2">
        <StatCard
          label="检测状态"
          :value="props.statusValue"
          :show-progress="props.isBatchProcessing"
          :processed-count="props.processedCount"
          :total-count="props.totalFilesToProcess"
        />
        <StatCard
          label="检测数量"
          :value="props.detectionCount"
        />
        <StatCard
          label="平均置信度"
          :value="props.avgConfidence"
        />
      </div>
    </div>

    <!-- Export Section -->
    <div class="px-4 py-3 border-t border-cyan-500/20 bg-slate-800/30 flex-shrink-0">
      <button
        @click="exportCurrent"
        :disabled="!canExportCurrent"
        class="w-full px-3 py-3 mb-2 text-sm font-semibold rounded-lg border-none cursor-pointer transition-all disabled:bg-slate-700/30 disabled:text-cyan-400/30 disabled:cursor-not-allowed"
        :class="canExportCurrent ? 'bg-gradient-to-r from-green-500 to-emerald-600 text-white hover:from-green-400 hover:to-emerald-500 hover:shadow-lg hover:shadow-green-500/30' : 'bg-slate-700/30 text-cyan-400/30'"
      >
        📥 导出当前结果
      </button>
      <button
        @click="batchExport"
        :disabled="!canBatchExport"
        class="w-full px-3 py-3 mb-2 text-sm font-semibold rounded-lg border-none cursor-pointer transition-all disabled:bg-slate-700/30 disabled:text-cyan-400/30 disabled:cursor-not-allowed"
        :class="canBatchExport ? 'bg-gradient-to-r from-cyan-500 to-blue-600 text-white hover:from-cyan-400 hover:to-blue-500 hover:shadow-lg hover:shadow-cyan-500/30' : 'bg-slate-700/30 text-cyan-400/30'"
      >
        📦 批量导出选中项 ({{ selectedCount }})
      </button>
      <button
        @click="stopBatchProcessing"
        :disabled="!isBatchProcessing"
        class="w-full px-3 py-2 text-sm font-semibold rounded-lg border-none cursor-pointer transition-all disabled:bg-slate-700/30 disabled:text-cyan-400/30 disabled:cursor-not-allowed"
        :class="isBatchProcessing ? 'bg-gradient-to-r from-yellow-500 to-orange-500 text-white hover:from-yellow-400 hover:to-orange-400 hover:shadow-lg hover:shadow-yellow-500/30' : 'bg-slate-700/30 text-cyan-400/30'"
      >
        ⏹ 停止批量处理
      </button>
      <div class="text-xs text-cyan-400/40 text-center mt-1.5">
        支持导出多个结果为 ZIP 包
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useDetectionState } from '@/composables/useDetectionState'
import { FILE_STATUS } from '@/utils/constants'
import StatCard from '@/components/shared/StatCard.vue'
import FileItem from '@/components/shared/FileItem.vue'

const props = defineProps({
  currentImagePath: {
    type: String,
    default: null
  },
  currentDetections: {
    type: Array,
    default: () => []
  },
  currentImageItem: {
    type: Object,
    default: null
  },
  statusValue: {
    type: String,
    default: '-'
  },
  detectionCount: {
    type: [Number, String],
    default: '-'
  },
  avgConfidence: {
    type: [Number, String],
    default: '-'
  },
  isBatchProcessing: {
    type: Boolean,
    default: false
  },
  processedCount: {
    type: Number,
    default: 0
  },
  totalFilesToProcess: {
    type: Number,
    default: 0
  }
})

const emit = defineEmits([
  'upload-files',
  'export-current',
  'batch-export',
  'stop-processing'
])

const state = useDetectionState()

// Refs
const fileInputRef = ref(null)
const folderInputRef = ref(null)

// Destructure state
const {
  availableModels,
  currentModelKey,
  pendingFiles,
  processedFiles,
  selectedFileItems,
  selectAllFiles,
  clearAllFilesSelection,
  toggleFileSelection,
  modelClasses,
  getClassColor
} = state

// Computed
const selectedCount = computed(() => selectedFileItems.value.size)

const currentModelName = computed(() => {
  const model = availableModels.value.find(m => m.key === currentModelKey.value)
  return model ? model.name : '未选择模型'
})

const currentModelDescription = computed(() => {
  const model = availableModels.value.find(m => m.key === currentModelKey.value)
  return model ? model.description : ''
})

const canExportCurrent = computed(() => {
  return props.currentDetections && props.currentDetections.length > 0
})

const canBatchExport = computed(() => {
  return selectedCount.value > 0
})

const classList = computed(() => {
  const classes = modelClasses.value
  if (!classes || Object.keys(classes).length === 0) return []

  return Object.entries(classes).map(([id, name]) => ({
    id: parseInt(id),
    name,
    color: getClassColor(parseInt(id)).stroke
  })).sort((a, b) => a.id - b.id)
})

// Methods
function triggerFileInput() {
  fileInputRef.value?.click()
}

function triggerFolderInput() {
  folderInputRef.value?.click()
}

function handleFileChange(event) {
  const files = Array.from(event.target.files)
  if (files.length > 0) {
    emit('upload-files', files)
  }
  // Reset input
  event.target.value = ''
}

function updateStats(result) {
  // This method is deprecated as we now use props
  // Kept for backward compatibility if needed, but should rely on props
}

function exportCurrent() {
  if (!canExportCurrent.value) {
    alert('没有可导出的数据！')
    return
  }
  emit('export-current')
}

function batchExport() {
  if (!canBatchExport.value) {
    alert('请先选择要导出的项目！')
    return
  }
  emit('batch-export')
}

function stopBatchProcessing() {
  emit('stop-processing')
}

// Expose methods
defineExpose({
  updateStats
})
</script>
