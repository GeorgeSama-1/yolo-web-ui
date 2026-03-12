<template>
  <div class="bg-white p-3 border-b border-gray-200 flex-shrink-0">
    <div class="flex items-center justify-between mb-2">
      <span class="text-xs font-semibold text-gray-700">选择检测模型</span>
      <span v-if="currentModel" class="text-primary text-xs">{{ currentModel.name }}</span>
      <span v-else class="text-gray-400 text-xs">加载中...</span>
    </div>

    <select
      :value="modelKey"
      :disabled="loading || models.length === 0"
      @change="handleChange"
      class="w-full px-3 py-2 border-2 border-gray-200 rounded-lg text-xs bg-white cursor-pointer transition-all hover:border-primary focus:outline-none focus:border-primary focus:ring-3 focus:ring-primary/10 disabled:opacity-50 disabled:cursor-not-allowed"
    >
      <option v-if="loading" value="" disabled>加载中...</option>
      <option v-else-if="models.length === 0" value="" disabled>无可用模型</option>
      <option
        v-for="model in models"
        :key="model.key"
        :value="model.key"
        :disabled="!model.exists"
      >
        {{ model.name }} - {{ model.description }}{{ !model.exists ? ' (文件不存在)' : '' }}
      </option>
    </select>

    <!-- Loading indicator -->
    <div v-if="loading" class="flex items-center justify-center gap-2 py-2 text-xs text-primary mt-2">
      <div class="w-4 h-4 border-2 border-gray-200 border-t-primary rounded-full animate-spin"></div>
      <span>正在加载模型...</span>
    </div>

    <!-- Status indicator -->
    <div v-else class="flex items-center gap-1.5 py-2 mt-2 text-xs" :class="statusClass">
      <div class="w-2 h-2 rounded-full" :class="statusDotClass"></div>
      <span>{{ statusText }}</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  models: {
    type: Array,
    default: () => []
  },
  modelKey: {
    type: String,
    default: null
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['change'])

const currentModel = computed(() => {
  return props.models.find(m => m.key === props.modelKey)
})

const hasError = computed(() => {
  return currentModel.value && !currentModel.value.exists
})

const statusClass = computed(() => ({
  'text-red-500': hasError.value,
  'text-green-600': !hasError.value
}))

const statusDotClass = computed(() => ({
  'bg-red-500': hasError.value,
  'bg-green-600': !hasError.value
}))

const statusText = computed(() => {
  if (hasError.value) return '模型文件不存在'
  if (currentModel.value) return `模型就绪 - ${currentModel.value.description}`
  return '模型就绪'
})

function handleChange(event) {
  emit('change', event.target.value)
}
</script>
