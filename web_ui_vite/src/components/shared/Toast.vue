<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition ease-out duration-300"
      enter-from-class="transform opacity-0 translate-y-[-20px]"
      enter-to-class="transform opacity-100 translate-y-0"
      leave-active-class="transition ease-in duration-200"
      leave-from-class="transform opacity-100 translate-y-0"
      leave-to-class="transform opacity-0 translate-y-[-20px]"
    >
      <div
        v-if="visible"
        class="fixed top-6 left-1/2 -translate-x-1/2 z-[9999] px-6 py-4 rounded-xl shadow-2xl flex items-center gap-3 min-w-[320px] max-w-md relative overflow-hidden"
        :class="typeClasses"
      >
        <!-- Progress bar background for loading type -->
        <div
          v-if="type === 'loading'"
          class="absolute bottom-0 left-0 h-1 bg-white/30 transition-all duration-300"
          :style="{ width: `${progressPercent}%` }"
        ></div>

        <!-- Animated shimmer for loading -->
        <div
          v-if="type === 'loading'"
          class="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent animate-shimmer"
        ></div>

        <span class="text-2xl flex-shrink-0 relative z-10">
          <span v-if="type === 'loading'" class="animate-spin">⚙</span>
          <span v-else>{{ icon }}</span>
        </span>
        <div class="flex-1 relative z-10">
          <div class="font-semibold" :class="textClasses">{{ title }}</div>
          <div v-if="message" class="text-sm mt-1 opacity-90" :class="textClasses">{{ message }}</div>
          <!-- Progress info for loading type -->
          <div v-if="type === 'loading' && progressCurrent !== undefined" class="text-sm mt-1 opacity-90" :class="textClasses">
            {{ progressCurrent }} / {{ progressTotal }}
            <span v-if="progressTotal > 0">({{ progressPercent.toFixed(0) }}%)</span>
          </div>
        </div>
        <button
          v-if="type !== 'loading'"
          @click="close"
          class="flex-shrink-0 opacity-70 hover:opacity-100 transition-opacity relative z-10"
          :class="textClasses"
        >
          ×
        </button>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  type: {
    type: String,
    default: 'info', // 'success', 'error', 'info', 'warning', 'loading'
    validator: (value) => ['success', 'error', 'info', 'warning', 'loading'].includes(value)
  },
  title: {
    type: String,
    required: true
  },
  message: {
    type: String,
    default: ''
  },
  duration: {
    type: Number,
    default: 3000
  },
  show: {
    type: Boolean,
    default: false
  },
  // Progress props for loading state
  progressCurrent: {
    type: Number,
    default: undefined
  },
  progressTotal: {
    type: Number,
    default: undefined
  }
})

const emit = defineEmits(['close'])

const visible = ref(false)

let timer = null

const typeClasses = computed(() => {
  const classes = {
    success: 'bg-gradient-to-r from-green-500 to-green-600',
    error: 'bg-gradient-to-r from-red-500 to-red-600',
    info: 'bg-gradient-to-r from-blue-500 to-blue-600',
    warning: 'bg-gradient-to-r from-yellow-500 to-orange-500',
    loading: 'bg-gradient-to-r from-cyan-500 to-blue-600'
  }
  return classes[props.type] || classes.info
})

const textClasses = computed(() => 'text-white')

const icon = computed(() => {
  const icons = {
    success: '✓',
    error: '✕',
    info: 'ℹ',
    warning: '⚠',
    loading: '⚙'
  }
  return icons[props.type] || icons.info
})

const progressPercent = computed(() => {
  if (props.progressTotal === undefined || props.progressTotal === 0) return 0
  if (props.progressCurrent === undefined) return 0
  return Math.min((props.progressCurrent / props.progressTotal) * 100, 100)
})

function close() {
  visible.value = false
  emit('close')
}

function startTimer() {
  if (timer) clearTimeout(timer)
  // Don't auto-close for loading type
  if (props.duration > 0 && props.type !== 'loading') {
    timer = setTimeout(() => {
      close()
    }, props.duration)
  }
}

watch(() => props.show, (newVal) => {
  visible.value = newVal
  if (newVal) {
    startTimer()
  } else if (timer) {
    clearTimeout(timer)
  }
}, { immediate: true })
</script>

<style scoped>
@keyframes shimmer {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

.animate-shimmer {
  animation: shimmer 1.5s infinite;
}
</style>
