<template>
  <div
    class="bg-white border rounded-lg p-2.5 mb-2 text-sm relative cursor-pointer"
    :class="statusClasses"
    @click="handleClick"
  >
    <input
      v-if="showCheckbox"
      type="checkbox"
      :checked="isSelected"
      @click.stop="toggleSelection"
      class="absolute top-2.5 right-2.5 w-4.5 h-4.5 cursor-pointer"
    >

    <div class="font-medium text-gray-700 mb-1 pr-8 break-words">{{ file.name }}</div>

    <!-- 显示检测结果 -->
    <div v-if="result" class="text-xs">
      <!-- 如果有类别统计，显示类别详情 -->
      <div v-if="result.class_counts && Object.keys(result.class_counts).length > 0" class="font-medium text-primary">
        <div class="flex items-center gap-1 flex-wrap">
          <span>检测:</span>
          <span
            v-for="(count, className) in result.class_counts"
            :key="className"
            class="px-1.5 py-0.5 rounded text-xs font-semibold text-white"
            :style="{ backgroundColor: getClassColorForName(className) }"
          >
            {{ className }}: {{ count }}
          </span>
        </div>
      </div>
      <!-- 否则显示总数（向后兼容） -->
      <div v-else class="font-medium text-primary">
        检测: {{ result.insulator_count || result.total_count || 0 }} 个
      </div>
    </div>

    <div class="text-xs text-gray-500 mt-0.5">{{ statusText }}</div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { FILE_STATUS } from '@/utils/constants'
import { useDetectionState } from '@/composables/useDetectionState'

const state = useDetectionState()

const props = defineProps({
  file: {
    type: Object,
    required: true
  },
  status: {
    type: String,
    default: FILE_STATUS.PENDING
  },
  result: {
    type: Object,
    default: null
  },
  showCheckbox: {
    type: Boolean,
    default: false
  },
  isSelected: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['click', 'toggle-selection'])

const statusClasses = computed(() => {
  return {
    'border-l-3 border-l-yellow-500': props.status === FILE_STATUS.PENDING,
    'border-l-3 border-l-primary bg-blue-50': props.status === FILE_STATUS.PROCESSING,
    'border-l-3 border-l-green-500': props.status === FILE_STATUS.COMPLETED,
    'border-l-3 border-l-red-500 bg-red-50': props.status === FILE_STATUS.ERROR,
    'border-gray-200': props.status === FILE_STATUS.PENDING || props.status === FILE_STATUS.PROCESSING
  }
})

const statusText = computed(() => {
  const statusMap = {
    [FILE_STATUS.PENDING]: '等待处理...',
    [FILE_STATUS.PROCESSING]: '正在检测...',
    [FILE_STATUS.COMPLETED]: '✓ 已完成',
    [FILE_STATUS.ERROR]: '✗ 失败'
  }
  return statusMap[props.status] || ''
})

// 根据类别名称获取颜色
function getClassColorForName(className) {
  // 从state中获取类别ID
  const modelClasses = state.modelClasses.value

  if (!modelClasses || Object.keys(modelClasses).length === 0) {
    // 如果没有类别信息，使用默认颜色
    console.warn('No model classes available, using default color')
    return '#3b82f6' // 蓝色
  }

  // 查找类别ID
  const classId = Object.keys(modelClasses).find(id => modelClasses[id] === className)

  if (classId !== undefined) {
    const classColor = state.getClassColor(parseInt(classId))
    return classColor.stroke
  }

  // 如果找不到类别，使用默认颜色
  console.warn(`Class "${className}" not found in model classes, using default color`)
  return '#3b82f6' // 蓝色
}

function handleClick() {
  emit('click')
}

function toggleSelection() {
  emit('toggle-selection')
}
</script>
