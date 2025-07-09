import {ref} from 'vue'

export function useNotifications() {
    const showSuccessMessage = ref(false)
    const showErrorMessage = ref(false)
    const showWarningMessage = ref(false)

    const successMessage = ref('')
    const errorMessage = ref('')
    const warningMessage = ref('')

    let successTimeout = null
    let errorTimeout = null
    let warningTimeout = null

    const showSuccess = (message = 'Operation successful') => {
        if (successTimeout) {
            clearTimeout(successTimeout)
        }

        successMessage.value = message
        showSuccessMessage.value = true

        successTimeout = setTimeout(() => {
            hideSuccess()
        }, 3000)
    }

    const showError = (message) => {
        if (errorTimeout) {
            clearTimeout(errorTimeout)
        }

        errorMessage.value = message
        showErrorMessage.value = true

        errorTimeout = setTimeout(() => {
            hideError()
        }, 5000)
    }

    const showWarning = (message) => {
        if (warningTimeout) {
            clearTimeout(warningTimeout)
        }

        warningMessage.value = message
        showWarningMessage.value = true

        warningTimeout = setTimeout(() => {
            hideWarning()
        }, 4000)
    }

    const hideSuccess = () => {
        if (successTimeout) {
            clearTimeout(successTimeout)
            successTimeout = null
        }
        showSuccessMessage.value = false
        successMessage.value = ''
    }

    const hideError = () => {
        if (errorTimeout) {
            clearTimeout(errorTimeout)
            errorTimeout = null
        }
        showErrorMessage.value = false
        errorMessage.value = ''
    }

    const hideWarning = () => {
        if (warningTimeout) {
            clearTimeout(warningTimeout)
            warningTimeout = null
        }
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
