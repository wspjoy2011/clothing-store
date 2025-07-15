import { ref } from 'vue'

export function usePasswordResetRequestState() {
    const formValid = ref(false)
    const resetFormRef = ref(null)
    const isRequesting = ref(false)
    const hasRequestError = ref(false)
    const requestErrorMessage = ref('')
    const requestSuccess = ref(false)

    const resetForm = () => {
        formValid.value = false
        isRequesting.value = false
        hasRequestError.value = false
        requestErrorMessage.value = ''
        requestSuccess.value = false

        if (resetFormRef.value) {
            resetFormRef.value.reset()
        }
    }

    const setRequestError = (message) => {
        hasRequestError.value = true
        requestErrorMessage.value = message
        requestSuccess.value = false
    }

    const setRequestSuccess = () => {
        hasRequestError.value = false
        requestErrorMessage.value = ''
        requestSuccess.value = true
    }

    const setRequesting = (value) => {
        isRequesting.value = value
    }

    return {
        formValid,
        resetFormRef,
        isRequesting,
        hasRequestError,
        requestErrorMessage,
        requestSuccess,
        resetForm,
        setRequestError,
        setRequestSuccess,
        setRequesting
    }
}
