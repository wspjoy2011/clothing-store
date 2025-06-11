import { ref } from 'vue'

export function useNotifications() {
  const showSuccessMessage = ref(false)
  const showErrorMessage = ref(false)
  const errorMessage = ref('')

  const showSuccess = (message = 'Operation successful') => {
    showSuccessMessage.value = true
  }

  const showError = (message) => {
    errorMessage.value = message
    showErrorMessage.value = true
  }

  const hideSuccess = () => {
    showSuccessMessage.value = false
  }

  const hideError = () => {
    showErrorMessage.value = false
    errorMessage.value = ''
  }

  return {
    showSuccessMessage,
    showErrorMessage,
    errorMessage,
    showSuccess,
    showError,
    hideSuccess,
    hideError
  }
}
