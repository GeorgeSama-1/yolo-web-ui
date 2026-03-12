<template>
  <div class="bg-slate-900/50 border border-cyan-500/20 rounded-lg p-2 text-center h-full flex flex-col justify-center">
    <div class="text-[10px] text-cyan-400/70 mb-0.5 truncate">{{ label }}</div>
    <div v-if="showProgress" class="flex flex-col items-center">
      <div class="text-sm font-bold text-cyan-400 mb-0.5">{{ processedCount }}/{{ totalCount }}</div>
      <div class="text-[10px] text-cyan-400/50">检测中...</div>
    </div>
    <div v-else class="text-sm font-bold text-cyan-50 truncate" :title="value">
      {{ value }}
    </div>
  </div>
</template>

<script setup>
defineProps({
  label: {
    type: String,
    required: true
  },
  value: {
    type: [String, Number],
    default: '-'
  },
  showProgress: {
    type: Boolean,
    default: false
  },
  processedCount: {
    type: Number,
    default: 0
  },
  totalCount: {
    type: Number,
    default: 0
  }
})
</script>
