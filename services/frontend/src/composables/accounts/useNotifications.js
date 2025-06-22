import {ref} from 'vue'

export function useNotifications() {
    const showSuccessMessage = ref(false)
    const showErrorMessage = ref(false)
    const showWarningMessage = ref(false)

    const successMessage = ref('')
    const errorMessage = ref('')
    const warningMessage = ref('')

    const showSuccess = (message = 'Operation successful') => {
        successMessage.value = message
        showSuccessMessage.value = true

        setTimeout(() => {
            hideSuccess()
        }, 3000)
    }

    const showError = (message) => {
        errorMessage.value = message
        showErrorMessage.value = true

        setTimeout(() => {
            hideError()
        }, 5000)
    }

    const showWarning = (message) => {
        warningMessage.value = message
        showWarningMessage.value = true

        setTimeout(() => {
            hideWarning()
        }, 4000)
    }

    const hideSuccess = () => {
        showSuccessMessage.value = false
        successMessage.value = ''
    }

    const hideError = () => {
        showErrorMessage.value = false
        errorMessage.value = ''
    }

    const hideWarning = () => {
        showWarningMessage.value = false
        warningMessage.value = ''
    }

    return {
        // State
        showSuccessMessage,
        showErrorMessage,
        showWarningMessage,
        successMessage,
        errorMessage,
        warningMessage,

        // Actions
        showSuccess,
        showError,
        showWarning,
        hideSuccess,
        hideError,
        hideWarning
    }
}
