import { ref, computed, watch } from 'vue'
import { useNotifications } from '@/composables/accounts/useNotifications.js'

export function useCardNotification() {
  const {
    showSuccess, showError, showWarning,
    showSuccessMessage, showErrorMessage, showWarningMessage,
    successMessage, errorMessage, warningMessage,
    hideSuccess, hideError, hideWarning
  } = useNotifications()

  const notificationType = ref(null)
  const notificationText = ref('')
  const activeNotification = ref(false)
  const progress = ref(100)
  const progressInterval = ref(null)
  const lastAction = ref(null)

  const notificationColor = computed(() => {
    if (notificationType.value === 'success' && lastAction.value === 'remove') {
      return '#d32f2f'
    }
    return undefined
  })

  watch(
    [showSuccessMessage, showErrorMessage, showWarningMessage],
    ([succ, err, warn]) => {
      if (succ) {
        notificationText.value = successMessage.value
        notificationType.value = 'success'
        runProgressBar(3000)
      } else if (err) {
        notificationText.value = errorMessage.value
        notificationType.value = 'error'
        runProgressBar(5000)
      } else if (warn) {
        notificationText.value = warningMessage.value
        notificationType.value = 'warning'
        runProgressBar(4000)
      } else {
        activeNotification.value = false
      }
    }
  )

  function runProgressBar(duration) {
    activeNotification.value = true
    progress.value = 100
    if (progressInterval.value) clearInterval(progressInterval.value)
    const step = 100 / (duration / 40)
    progressInterval.value = setInterval(() => {
      progress.value -= step
      if (progress.value <= 0) {
        progress.value = 0
        activeNotification.value = false
        clearInterval(progressInterval.value)
      }
    }, 40)
  }

  function closeNotification() {
    activeNotification.value = false
    hideSuccess()
    hideError()
    hideWarning()
    if (progressInterval.value) clearInterval(progressInterval.value)
  }

  function showAddSuccess() {
    lastAction.value = 'add'
    showSuccess('Product added')
  }
  function showRemoveSuccess() {
    lastAction.value = 'remove'
    showSuccess('Product removed from cart')
  }

  return {
    notificationType,
    notificationText,
    activeNotification,
    progress,
    notificationColor,
    closeNotification,
    showAddSuccess,
    showRemoveSuccess,
    showError,
    showWarning
  }
}
