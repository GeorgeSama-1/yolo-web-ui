<template>
  <div
    class="bg-slate-800/50 border border-cyan-500/20 rounded-lg p-2.5 mb-2 cursor-pointer transition-all hover:border-cyan-500/50 hover:shadow-lg hover:shadow-cyan-500/10 relative flex items-center gap-2"
    :class="{
      'border-cyan-500 bg-cyan-950/30': isActive,
      'border-l-4 border-l-green-500 bg-green-950/20': markStatus === 'pass',
      'border-l-4 border-l-red-500 bg-red-950/20': markStatus === 'fail'
    }"
    @click="handleClick"
  >
    <!-- Checkbox -->
    <input
      type="checkbox"
      :checked="isSelected"
      @click.stop="toggleSelection"
      class="flex-shrink-0 w-4 h-4 cursor-pointer accent-cyan-500"
    >

    <!-- Mark Status Icon -->
    <div
      v-if="markStatus !== 'none'"
      class="flex-shrink-0 w-5 h-5 rounded-full flex items-center justify-center text-white text-xs font-bold"
      :class="{
        'bg-green-500 shadow-lg shadow-green-500/50': markStatus === 'pass',
        'bg-red-500 shadow-lg shadow-red-500/50': markStatus === 'fail'
      }"
    >
      {{ markStatus === 'pass' ? '✓' : '✗' }}
    </div>

    <!-- Content -->
    <div class="flex-1 min-w-0 flex flex-col gap-1">
      <!-- Name -->
      <span class="text-sm font-medium text-cyan-50 truncate w-full" :title="item.imageName">
        {{ item.imageName }}
      </span>

      <!-- Info Row -->
      <div class="flex items-center gap-1.5">
        <!-- Model Badge -->
        <span
          v-if="item.modelInfo"
          class="bg-cyan-950/50 text-cyan-400 border border-cyan-500/30 px-1.5 py-0.5 rounded text-[10px] font-medium flex-shrink-0 truncate max-w-[80px]"
          :title="item.modelInfo.name"
        >
          {{ item.modelInfo.name }}
        </span>

        <!-- Count -->
        <span class="text-xs text-cyan-400/70 font-medium whitespace-nowrap flex-shrink-0">
          {{ item.count }}个
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { MARK_STATUS } from '@/utils/constants'

const props = defineProps({
  item: {
    type: Object,
    required: true
  },
  index: {
    type: Number,
    required: true
  },
  isActive: {
    type: Boolean,
    default: false
  },
  isSelected: {
    type: Boolean,
    default: false
  },
  historyStatus: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['click', 'toggle-selection'])

const markStatus = computed(() => {
  return props.historyStatus[props.item.id] || MARK_STATUS.NONE
})

function handleClick() {
  emit('click', props.index)
}

function toggleSelection() {
  emit('toggle-selection', props.index)
}
</script>
