import { reactive } from 'vue'

// Global toast state (shared across all components)
const toast = reactive({
  show: false,
  type: 'info',
  title: '',
  message: '',
  duration: 3000
})

// Unique ID for tracking
let toastId = 0

export function useToast() {
  function showToast(options) {
    // If options is a string, treat it as title with type 'info'
    if (typeof options === 'string') {
      options = { title: options, type: 'info' }
    }

    const {
      type = 'info',
      title = '',
      message = '',
      duration = 3000
    } = options

    // Increment ID to force reactivity
    toastId++

    toast.type = type
    toast.title = title
    toast.message = message
    toast.duration = duration
    toast.show = true

    // Auto-hide after duration
    if (duration > 0) {
      setTimeout(() => {
        toast.show = false
      }, duration)
    }
  }

  function showSuccess(title, message = '', duration = 3000) {
    showToast({ type: 'success', title, message, duration })
  }

  function showError(title, message = '', duration = 4000) {
    showToast({ type: 'error', title, message, duration })
  }

  function showInfo(title, message = '', duration = 3000) {
    showToast({ type: 'info', title, message, duration })
  }

  function showWarning(title, message = '', duration = 3500) {
    showToast({ type: 'warning', title, message, duration })
  }

  function hide() {
    toast.show = false
  }

  return {
    toast,
    showToast,
    showSuccess,
    showError,
    showInfo,
    showWarning,
    hide
  }
}
