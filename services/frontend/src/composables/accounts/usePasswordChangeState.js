import { ref } from 'vue'

export function usePasswordChangeState() {
    const formValid = ref(false)
    const changeFormRef = ref(null)
    const isChanging = ref(false)
    const hasChangeError = ref(false)
    const changeErrorMessage = ref('')
    const changeSuccess = ref(false)

    const setChangeError = (error) => {
        hasChangeError.value = true
        changeErrorMessage.value = error
        changeSuccess.value = false
    }

    const setChangeSuccess = () => {
        changeSuccess.value = true
        hasChangeError.value = false
        changeErrorMessage.value = ''
    }

    const setChanging = (loading) => {
        isChanging.value = loading
    }

    const resetForm = () => {
        formValid.value = false
        isChanging.value = false
        hasChangeError.value = false
        changeErrorMessage.value = ''
        changeSuccess.value = false
        if (changeFormRef.value) {
            changeFormRef.value.resetValidation()
        }
    }

    return {
        formValid,
        changeFormRef,
        isChanging,
        hasChangeError,
        changeErrorMessage,
        changeSuccess,
        resetForm,
        setChangeError,
        setChangeSuccess,
        setChanging
    }
}
