import { ref } from 'vue'
import { usePasswordValidation } from '@/composables/accounts/usePasswordValidation'
import { usePasswordResetConfirmState } from '@/composables/accounts/usePasswordResetConfirmState'
import { usePasswordResetConfirmActions } from '@/composables/accounts/usePasswordResetConfirmActions'
import { useThemeState } from '@/composables/useThemeState'
import { usePageTitle } from '@/composables/usePageTitle'

export function usePasswordResetConfirmPage(props) {
    const { isDarkTheme } = useThemeState()
    usePageTitle('StyleShop - Reset Password')

    const token = ref(props.token)

    const {
        password,
        confirmPassword,
        showPassword,
        showConfirmPassword,
        passwordRules,
        confirmPasswordRules,
        resetPasswordValidation
    } = usePasswordValidation()

    const {
        formValid,
        confirmFormRef,
        isConfirming,
        hasConfirmError,
        confirmErrorMessage,
        confirmSuccess,
        isLoading,
        resetForm: baseResetForm,
        setConfirmError,
        setConfirmSuccess,
        setConfirming,
        setLoading
    } = usePasswordResetConfirmState()

    const {
        handlePasswordResetConfirm: baseHandlePasswordResetConfirm,
        goToLogin,
        goToPasswordReset,
        goToRegister
    } = usePasswordResetConfirmActions()

    const handlePasswordResetConfirm = async () => {
        await baseHandlePasswordResetConfirm(token, password, formValid, {
            setConfirmError,
            setConfirmSuccess,
            setConfirming
        })
    }

    const resetFormData = () => {
        baseResetForm()
        resetPasswordValidation()
    }

    return {
        isDarkTheme,
        token,
        password,
        confirmPassword,
        showPassword,
        showConfirmPassword,
        passwordRules,
        confirmPasswordRules,
        formValid,
        confirmForm: confirmFormRef,
        isConfirming,
        hasConfirmError,
        confirmErrorMessage,
        confirmSuccess,
        isLoading,
        handlePasswordResetConfirm,
        resetFormData,
        goToLogin,
        goToPasswordReset,
        goToRegister
    }
}
