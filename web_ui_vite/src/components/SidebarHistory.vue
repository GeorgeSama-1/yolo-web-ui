<template>
  <div class="h-full flex flex-col">
    <!-- Header Actions -->
    <div class="px-3 py-3 bg-slate-800/30 border-b border-cyan-500/20 flex gap-2 flex-shrink-0">
      <button
        @click="selectAllHistory"
        class="flex-1 px-3 py-2 text-xs font-semibold border border-cyan-500/30 rounded-lg bg-slate-700/50 text-cyan-400 cursor-pointer transition-all duration-300 hover:bg-cyan-500/20 hover:border-cyan-500/50 hover:shadow-lg hover:shadow-cyan-500/10 flex items-center justify-center gap-1.5 relative overflow-hidden group"
        title="全选"
      >
        <span class="text-sm relative z-10">☑</span>
        <span class="relative z-10">全选</span>
        <div class="absolute inset-0 bg-gradient-to-r from-transparent via-cyan-400/20 to-transparent -translate-x-full group-hover:animate-shimmer"></div>
      </button>
      <button
        @click="clearAllHistory"
        class="flex-1 px-3 py-2 text-xs font-semibold border border-cyan-500/30 rounded-lg bg-slate-700/50 text-cyan-400 cursor-pointer transition-all duration-300 hover:bg-cyan-500/20 hover:border-cyan-500/50 hover:shadow-lg hover:shadow-cyan-500/10 flex items-center justify-center gap-1.5 relative overflow-hidden group"
        title="清空列表"
      >
        <span class="text-sm relative z-10">🗑</span>
        <span class="relative z-10">清空</span>
        <div class="absolute inset-0 bg-gradient-to-r from-transparent via-cyan-400/20 to-transparent -translate-x-full group-hover:animate-shimmer"></div>
      </button>
      <button
        @click="clearAllMarks"
        class="flex-1 px-3 py-2 text-xs font-semibold border border-cyan-500/30 rounded-lg bg-slate-700/50 text-cyan-400 cursor-pointer transition-all duration-300 hover:bg-cyan-500/20 hover:border-cyan-500/50 hover:shadow-lg hover:shadow-cyan-500/10 flex items-center justify-center gap-1.5 relative overflow-hidden group"
        title="清除标记"
      >
        <span class="text-sm relative z-10">↶</span>
        <span class="relative z-10">清除</span>
        <div class="absolute inset-0 bg-gradient-to-r from-transparent via-cyan-400/20 to-transparent -translate-x-full group-hover:animate-shimmer"></div>
      </button>
    </div>

    <div class="px-3 py-2 bg-slate-800/20 border-b border-cyan-500/20 flex-shrink-0">
      <button
        @click="clearAllHistory"
        class="w-full px-3 py-2 text-sm font-semibold border border-orange-500/30 rounded-lg bg-orange-950/30 text-orange-400 cursor-pointer transition-all hover:bg-orange-950/50 hover:border-orange-500/50 hover:shadow-lg hover:shadow-orange-500/20 flex items-center justify-center gap-2"
      >
        <span class="text-base">🗑️</span>
        <span>清空所有历史</span>
      </button>
    </div>

    <div class="px-3 py-2 bg-slate-800/20 border-b border-cyan-500/20 flex-shrink-0">
      <button
        @click="deleteSelectedHistory"
        class="w-full px-3 py-2 text-sm font-semibold border border-red-500/30 rounded-lg bg-red-950/30 text-red-400 cursor-pointer transition-all hover:bg-red-950/50 hover:border-red-500/50 hover:shadow-lg hover:shadow-red-500/20 flex items-center justify-center gap-2"
      >
        <span class="text-base">✕</span>
        <span>删除选中</span>
      </button>
    </div>

    <!-- Filter Bar -->
    <div class="px-3 py-2.5 bg-slate-800/30 border-b border-cyan-500/20 flex flex-wrap gap-2.5 items-center flex-shrink-0">
      <!-- Model Filter -->
      <div class="flex items-center gap-2">
        <label class="text-xs text-cyan-400/80">模型:</label>
        <select
          :value="modelFilter"
          @change="updateFilter('modelFilter', $event.target.value)"
          class="px-2.5 py-1.5 rounded-lg border border-cyan-500/30 bg-slate-900/50 text-xs text-cyan-50 min-w-45 focus:outline-none focus:border-cyan-500/50"
        >
          <option value="all">全部模型</option>
          <option
            v-for="model in availableModels"
            :key="model.key"
            :value="model.key"
          >
            {{ model.name }} - {{ model.description }}
          </option>
        </select>
      </div>

      <!-- Count Filter -->
      <div class="flex items-center gap-2">
        <input
          type="checkbox"
          :checked="enableCountFilter"
          @change="updateFilter('enableCountFilter', $event.target.checked)"
          class="cursor-pointer accent-cyan-500"
        >
        <span class="text-xs text-cyan-400/80">显示数量 < </span>
        <input
          type="number"
          :value="countThreshold"
          @change="updateFilter('countThreshold', parseInt($event.target.value) || 70)"
          min="0"
          max="1000"
          class="w-17.5 px-1.5 py-1.5 rounded-lg border border-cyan-500/30 bg-slate-900/50 text-xs text-cyan-50 focus:outline-none focus:border-cyan-500/50"
        >
        <span class="text-xs text-cyan-400/80"> 的图片</span>
      </div>

      <!-- Filtered Count -->
      <div class="ml-auto text-xs text-cyan-400/50">
        <template v-if="filteredCount < totalCount">
          (显示 {{ filteredCount }}/{{ totalCount }} 项)
        </template>
      </div>
    </div>

    <!-- Model Comparison Button -->
    <div class="px-3 py-2.5 bg-slate-800/20 border-b border-cyan-500/20 text-center flex-shrink-0">
      <button
        @click="openComparisonPanel"
        class="w-full px-3 py-2 text-sm font-semibold rounded-lg border-none cursor-pointer bg-gradient-to-r from-cyan-500 to-blue-600 text-white transition-all hover:from-cyan-400 hover:to-blue-500 hover:shadow-lg hover:shadow-cyan-500/30"
      >
        📊 模型对比
      </button>
    </div>

    <!-- History List -->
    <div class="flex-1 overflow-y-auto px-3 py-2.5">
      <div v-if="folderGroupedHistory.length === 0" class="px-5 py-5 text-center text-cyan-400/30 text-sm">
        暂无记录
      </div>

      <!-- Folder Groups -->
      <div v-for="group in folderGroupedHistory" :key="group.folderName" class="mb-2.5 border border-cyan-500/20 rounded-lg bg-slate-800/30 overflow-hidden">
        <!-- Folder Header -->
        <div
          class="flex items-center px-3 py-2 bg-slate-700/30 border-b border-cyan-500/20 cursor-pointer select-none transition-all"
          :class="{ 'bg-gradient-to-r from-cyan-600 to-blue-600': group.expanded }"
          @click="toggleFolder(group.folderName)"
        >
          <span class="mr-1.5 text-[10px] transition-transform" :class="{ 'rotate-90': group.expanded }">▶</span>
          <span class="flex-1 text-xs font-semibold truncate" :class="group.expanded ? 'text-white' : 'text-cyan-50'" :title="group.folderName === 'root' ? '根目录' : group.folderName">📁 {{ group.folderName === 'root' ? '根目录' : group.folderName }}</span>
          <span class="text-[10px]" :class="{ 'text-white/80': group.expanded, 'text-cyan-400/60': !group.expanded }">({{ group.items.length }})</span>
        </div>

        <!-- Folder Items -->
        <div v-show="group.expanded" class="px-2 py-2 bg-slate-900/30">
          <HistoryItem
            v-for="(item, idx) in group.items"
            :key="item.originalIndex"
            :item="item"
            :index="item.originalIndex"
            :is-active="item.originalIndex === activeIndex"
            :is-selected="selectedHistoryItems.has(item.originalIndex)"
            :history-status="historyStatus"
            @click="loadFromHistory"
            @toggle-selection="toggleHistorySelection"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useDetectionState } from '@/composables/useDetectionState'
import HistoryItem from '@/components/shared/HistoryItem.vue'

const state = useDetectionState()

// Destructure state
const {
  filteredHistory,
  history,
  selectedHistoryItems,
  historyStatus,
  folderExpandedState,
  availableModels,
  modelFilter,
  enableCountFilter,
  countThreshold,
  selectAllHistory,
  clearAllHistorySelection,
  clearAllMarks,
  clearHistory,
  toggleHistorySelection,
  toggleFolder,
  loadFromHistory,
  setFilters
} = state

// Emit for parent actions
const emit = defineEmits(['delete-selected', 'open-comparison', 'clear-history'])

// Computed
const totalCount = computed(() => history.value.length)

const filteredCount = computed(() => filteredHistory.value.length)

const folderGroupedHistory = computed(() => {
  const groups = {}

  filteredHistory.value.forEach((item, index) => {
    const folder = item.folderName || 'root'
    if (!groups[folder]) {
      groups[folder] = []
    }
    // Find original index in the global history array
    // This is crucial because loadFromHistory expects the index in state.history.value
    // Since objects are references, we can use indexOf
    const originalIndex = history.value.indexOf(item)

    // Store original index for proper selection handling
    groups[folder].push({ ...item, originalIndex: originalIndex })
  })

  // Initialize folder expanded state for new folders
  Object.keys(groups).forEach(folder => {
    if (folderExpandedState.value[folder] === undefined) {
      folderExpandedState.value[folder] = true
    }
  })

  // Clean up expanded state for deleted folders
  Object.keys(folderExpandedState.value).forEach(folder => {
    if (!groups[folder]) {
      delete folderExpandedState.value[folder]
    }
  })

  return Object.entries(groups).map(([folderName, items]) => ({
    folderName,
    items,
    expanded: folderExpandedState.value[folderName] !== false
  }))
})

// Track active index
const activeIndex = computed(() => {
  // Find the index of currently loaded item
  return -1 // This will be managed by parent component
})

// Methods
function updateFilter(key, value) {
  setFilters({ [key]: value })
}

function deleteSelectedHistory() {
  if (selectedHistoryItems.value.size === 0) {
    alert('请先选择要删除的记录！')
    return
  }

  if (!confirm(`确定要删除选中的 ${selectedHistoryItems.value.size} 条记录吗？`)) {
    return
  }

  emit('delete-selected', Array.from(selectedHistoryItems.value))
}

function openComparisonPanel() {
  emit('open-comparison')
}

function clearAllHistory() {
  if (history.value.length === 0) {
    alert('暂无历史记录！')
    return
  }

  if (!confirm(`确定要清空所有历史记录吗？共 ${history.value.length} 条记录将被删除。`)) {
    return
  }

  emit('clear-history')
}
</script>

<style scoped>
@keyframes shimmer {
  100% {
    transform: translateX(100%);
  }
}

.group:hover .animate-shimmer {
  animation: shimmer 1.5s infinite;
}
</style>
