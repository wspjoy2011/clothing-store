import {ref} from 'vue'

export function usePasswordResetConfirmState() {
    const formValid = ref(false)
    const confirmFormRef = ref(null)
    const isConfirming = ref(false)
    const hasConfirmError = ref(false)
    const confirmErrorMessage = ref('')
    const confirmSuccess = ref(false)
    const isLoading = ref(false)

    const resetForm = () => {
        formValid.value = false
        isConfirming.value = false
        hasConfirmError.value = false
        confirmErrorMessage.value = ''
        confirmSuccess.value = false
        isLoading.value = false

        if (confirmFormRef.value) {
            confirmFormRef.value.reset()
        }
    }

    const setConfirmError = (message) => {
        hasConfirmError.value = true
        confirmErrorMessage.value = message
        confirmSuccess.value = false
    }

    const setConfirmSuccess = () => {
        hasConfirmError.value = false
        confirmErrorMessage.value = ''
        confirmSuccess.value = true
    }

    const setConfirming = (value) => {
        isConfirming.value = value
    }

    const setLoading = (value) => {
        isLoading.value = value
    }

    return {
        formValid,
        confirmFormRef,
        isConfirming,
        hasConfirmError,
        confirmErrorMessage,
        confirmSuccess,
        isLoading,
        resetForm,
        setConfirmError,
        setConfirmSuccess,
        setConfirming,
        setLoading
    }
}
