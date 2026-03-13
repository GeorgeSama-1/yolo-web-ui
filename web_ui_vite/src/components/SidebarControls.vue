<template>
  <div class="h-full flex flex-col bg-slate-950/70">
    <div class="flex-1 overflow-y-auto px-4 py-4 space-y-4">
      <section class="rounded-2xl border border-cyan-500/20 bg-slate-900/80 p-4 shadow-lg shadow-cyan-950/20">
        <div class="flex items-center justify-between gap-3 mb-3">
          <div>
            <div class="text-[11px] font-semibold uppercase tracking-[0.24em] text-cyan-400/80">Model</div>
            <h3 class="text-sm font-semibold text-cyan-50 mt-1">当前模型</h3>
          </div>
          <span class="inline-flex items-center gap-1 rounded-full border border-cyan-500/30 bg-cyan-500/10 px-2 py-1 text-[10px] text-cyan-300">
            <span class="h-1.5 w-1.5 rounded-full bg-cyan-400"></span>
            在线
          </span>
        </div>

        <label class="block text-xs font-medium text-cyan-200 mb-2">切换模型</label>
        <select
          :value="currentModelKey || ''"
          :disabled="isModelSwitching || availableModels.length === 0"
          class="w-full rounded-xl border border-cyan-500/20 bg-slate-950/90 px-3 py-2.5 text-sm text-cyan-50 outline-none transition focus:border-cyan-400 focus:ring-2 focus:ring-cyan-500/30 disabled:cursor-not-allowed disabled:opacity-50"
          @change="handleModelChange($event.target.value)"
        >
          <option disabled value="">
            {{ availableModels.length === 0 ? '暂无可用模型' : '请选择模型' }}
          </option>
          <option
            v-for="model in availableModels"
            :key="model.key"
            :value="model.key"
          >
            {{ model.name }}
          </option>
        </select>

        <div class="mt-3 rounded-xl border border-cyan-500/10 bg-slate-900/50 px-3 py-3">
          <div class="text-sm font-medium text-cyan-50 truncate" :title="currentModelName">
            {{ currentModelName }}
          </div>
          <div class="text-xs text-cyan-400/70 mt-1 leading-relaxed" :title="currentModelDescription">
            {{ currentModelDescription }}
          </div>
          <div v-if="isModelSwitching" class="mt-2 text-xs text-amber-300">
            正在切换模型...
          </div>
        </div>
      </section>

      <section class="rounded-2xl border border-emerald-500/15 bg-slate-900/80 p-4 shadow-lg shadow-slate-950/20">
        <div class="text-[11px] font-semibold uppercase tracking-[0.24em] text-emerald-300/70">Status</div>
        <h3 class="text-sm font-semibold text-cyan-50 mt-1 mb-3">当前状态</h3>
        <div class="grid grid-cols-1 gap-2.5">
          <StatCard
            label="检测状态"
            :value="props.statusValue"
            :show-progress="props.isBatchProcessing"
            :processed-count="props.processedCount"
            :total-count="props.totalFilesToProcess"
          />
          <div class="grid grid-cols-2 gap-2.5">
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
      </section>

      <section class="rounded-2xl border border-amber-500/20 bg-slate-900/80 p-4">
        <div class="text-[11px] font-semibold uppercase tracking-[0.24em] text-amber-300/70">Current Image</div>
        <div class="flex items-start justify-between gap-3 mt-1 mb-3">
          <div>
            <h3 class="text-sm font-semibold text-cyan-50">重新检测当前图片</h3>
            <p class="text-xs text-slate-400 mt-1 leading-relaxed">
              只对当前图片这一次重新检测生效，不影响后续上传和批量处理。
            </p>
            <p class="text-xs text-slate-500 mt-1">默认：confidence 0.80 / IoU 0.30</p>
          </div>
          <span class="rounded-full bg-slate-800 px-2 py-1 text-[10px] text-slate-300">
            {{ currentImageLabel }}
          </span>
        </div>

        <div class="space-y-4">
          <div>
            <label class="mb-2 block text-sm font-medium text-cyan-100">
              置信度阈值: <span class="font-semibold">{{ redetectConfidence.toFixed(2) }}</span>
            </label>
            <input
              data-testid="redetect-confidence"
              v-model.number="redetectConfidence"
              type="range"
              min="0.1"
              max="0.95"
              step="0.01"
              class="h-2 w-full cursor-pointer appearance-none rounded-lg bg-slate-700"
            >
          </div>

          <div>
            <label class="mb-2 block text-sm font-medium text-cyan-100">
              IoU 阈值: <span class="font-semibold">{{ redetectIou.toFixed(2) }}</span>
            </label>
            <input
              data-testid="redetect-iou"
              v-model.number="redetectIou"
              type="range"
              min="0.1"
              max="0.9"
              step="0.01"
              class="h-2 w-full cursor-pointer appearance-none rounded-lg bg-slate-700"
            >
          </div>
        </div>

        <div class="mt-4 grid grid-cols-1 gap-2">
          <button
            data-testid="redetect-current-button"
            :disabled="!currentImagePath || isRedetecting"
            class="w-full rounded-xl bg-amber-500 px-3 py-2.5 text-sm font-semibold text-white transition hover:bg-amber-400 disabled:cursor-not-allowed disabled:bg-slate-700 disabled:text-slate-400"
            @click="redetectCurrentImage"
          >
            {{ isRedetecting ? '重新检测中...' : '重新检测当前图片' }}
          </button>
          <button
            data-testid="reset-redetect-thresholds"
            class="w-full rounded-xl border border-slate-600 bg-slate-800 px-3 py-2 text-sm font-semibold text-slate-200 transition hover:border-slate-500 hover:bg-slate-700"
            @click="resetRedetectThresholds"
          >
            恢复默认阈值
          </button>
        </div>
      </section>

      <section class="rounded-2xl border border-cyan-500/20 bg-slate-900/80 p-4">
        <div class="text-[11px] font-semibold uppercase tracking-[0.24em] text-cyan-300/70">Upload</div>
        <h3 class="text-sm font-semibold text-cyan-50 mt-1 mb-3">上传操作</h3>
        <div class="grid grid-cols-2 gap-2">
          <button
            class="rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 px-3 py-2.5 text-sm font-semibold text-white transition hover:from-cyan-400 hover:to-blue-500"
            @click="triggerFileInput"
          >
            选择文件
          </button>
          <button
            class="rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 px-3 py-2.5 text-sm font-semibold text-white transition hover:from-cyan-400 hover:to-blue-500"
            @click="triggerFolderInput"
          >
            文件夹
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
      </section>

      <section v-if="classList.length > 0" class="rounded-2xl border border-violet-500/20 bg-slate-900/80 p-4">
        <div class="text-[11px] font-semibold uppercase tracking-[0.24em] text-violet-300/70">Classes</div>
        <h3 class="text-sm font-semibold text-cyan-50 mt-1 mb-3">检测类别</h3>
        <div class="grid grid-cols-1 gap-2">
          <div
            v-for="cls in classList"
            :key="cls.id"
            class="flex items-center gap-3 rounded-xl border border-slate-800 bg-slate-950/70 px-3 py-2"
          >
            <span
              class="h-3 w-3 rounded-full"
              :style="{ backgroundColor: cls.color }"
            ></span>
            <div class="min-w-0 flex-1">
              <div class="truncate text-sm text-cyan-50">{{ cls.name }}</div>
              <div class="text-[11px] text-slate-500">class_{{ cls.id }}</div>
            </div>
          </div>
        </div>
      </section>

      <section class="rounded-2xl border border-emerald-500/20 bg-slate-900/80 p-4">
        <div class="text-[11px] font-semibold uppercase tracking-[0.24em] text-emerald-300/70">Export</div>
        <h3 class="text-sm font-semibold text-cyan-50 mt-1 mb-3">导出操作</h3>
        <div class="grid grid-cols-1 gap-2">
          <button
            :disabled="!canExportCurrent"
            class="w-full rounded-xl bg-gradient-to-r from-green-500 to-emerald-600 px-3 py-3 text-sm font-semibold text-white transition hover:from-green-400 hover:to-emerald-500 disabled:cursor-not-allowed disabled:bg-slate-700 disabled:text-slate-400"
            @click="exportCurrent"
          >
            导出当前结果
          </button>
          <button
            :disabled="!canBatchExport"
            class="w-full rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 px-3 py-3 text-sm font-semibold text-white transition hover:from-cyan-400 hover:to-blue-500 disabled:cursor-not-allowed disabled:bg-slate-700 disabled:text-slate-400"
            @click="batchExport"
          >
            批量导出选中项 ({{ selectedCount }})
          </button>
          <button
            :disabled="!isBatchProcessing"
            class="w-full rounded-xl bg-gradient-to-r from-yellow-500 to-orange-500 px-3 py-2.5 text-sm font-semibold text-white transition hover:from-yellow-400 hover:to-orange-400 disabled:cursor-not-allowed disabled:bg-slate-700 disabled:text-slate-400"
            @click="stopBatchProcessing"
          >
            停止批量处理
          </button>
        </div>
      </section>
    </div>

    <div class="border-t border-red-500/20 bg-slate-950/95 px-4 py-3">
      <div class="rounded-2xl border border-red-500/20 bg-red-500/5 p-4">
        <div class="text-[11px] font-semibold uppercase tracking-[0.24em] text-red-300/70">Danger Zone</div>
        <h3 class="text-sm font-semibold text-red-100 mt-1">数据管理</h3>
        <p class="mt-1 text-xs leading-relaxed text-red-100/70">
          清空所有上传图片和导出文件，不会删除你左侧已经查看过的本地历史显示。
        </p>
        <button
          class="mt-3 w-full rounded-xl bg-red-500 px-3 py-2.5 text-sm font-semibold text-white transition hover:bg-red-400"
          @click="clearAllUploads"
        >
          清空所有文件
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useDetectionState } from '@/composables/useDetectionState'
import StatCard from '@/components/shared/StatCard.vue'

const DEFAULT_REDETECT_CONFIDENCE = 0.8
const DEFAULT_REDETECT_IOU = 0.3

const props = defineProps({
  currentImagePath: {
    type: String,
    default: null
  },
  currentImageName: {
    type: String,
    default: null
  },
  currentDetections: {
    type: Array,
    default: () => []
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
  },
  isRedetecting: {
    type: Boolean,
    default: false
  },
  isModelSwitching: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits([
  'upload-files',
  'export-current',
  'batch-export',
  'stop-processing',
  'model-changed',
  'redetect-current',
  'clear-all-uploads'
])

const state = useDetectionState()

const fileInputRef = ref(null)
const folderInputRef = ref(null)
const redetectConfidence = ref(DEFAULT_REDETECT_CONFIDENCE)
const redetectIou = ref(DEFAULT_REDETECT_IOU)

const {
  availableModels,
  currentModelKey,
  modelClasses,
  getClassColor,
  selectedCount: totalSelectedCount
} = state

const selectedCount = computed(() => totalSelectedCount.value)

const currentModelName = computed(() => {
  const model = availableModels.value.find(item => item.key === currentModelKey.value)
  return model ? model.name : '未选择模型'
})

const currentModelDescription = computed(() => {
  const model = availableModels.value.find(item => item.key === currentModelKey.value)
  return model ? model.description : '请先选择一个可用模型'
})

const currentImageLabel = computed(() => props.currentImageName || '未选择图片')

const canExportCurrent = computed(() => props.currentDetections && props.currentDetections.length > 0)
const canBatchExport = computed(() => selectedCount.value > 0)

const classList = computed(() => {
  const classes = modelClasses.value
  if (!classes || Object.keys(classes).length === 0) {
    return []
  }

  return Object.entries(classes)
    .map(([id, name]) => ({
      id: Number(id),
      name,
      color: getClassColor(Number(id)).stroke
    }))
    .sort((left, right) => left.id - right.id)
})

function triggerFileInput() {
  fileInputRef.value?.click()
}

function triggerFolderInput() {
  folderInputRef.value?.click()
}

function handleFileChange(event) {
  const files = Array.from(event.target.files || [])
  if (files.length > 0) {
    emit('upload-files', files)
  }
  event.target.value = ''
}

function handleModelChange(modelKey) {
  if (!modelKey || modelKey === currentModelKey.value || props.isModelSwitching) {
    return
  }
  emit('model-changed', modelKey)
}

function redetectCurrentImage() {
  if (!props.currentImagePath || props.isRedetecting) {
    return
  }

  emit('redetect-current', {
    confidenceThreshold: redetectConfidence.value,
    iouThreshold: redetectIou.value
  })
}

function resetRedetectThresholds() {
  redetectConfidence.value = DEFAULT_REDETECT_CONFIDENCE
  redetectIou.value = DEFAULT_REDETECT_IOU
}

function clearAllUploads() {
  emit('clear-all-uploads')
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
</script>
