import { useRouter } from 'vue-router'
import { useAccountStore } from '@/stores/accounts'
import { useNotifications } from '@/composables/accounts/useNotifications'

export function usePasswordResetRequestActions() {
    const router = useRouter()
    const accountStore = useAccountStore()
    const { showSuccess, showError } = useNotifications()

    const handlePasswordResetRequest = async (email, formValid, { setRequestError, setRequestSuccess, setRequesting }) => {
        if (!formValid.value) return

        setRequesting(true)

        try {
            const result = await accountStore.requestPasswordReset({ email: email.value })

            if (result.success) {
                setRequestSuccess()
                showSuccess('If an account with that email exists, we\'ve sent you a password reset link.')
            } else {
                setRequestError(result.message || 'Failed to send password reset email')
                showError(result.message || 'Failed to send password reset email')
            }
        } catch (error) {
            setRequestError('An unexpected error occurred')
            showError('An unexpected error occurred')
        } finally {
            setRequesting(false)
        }
    }

    const goToLogin = () => {
        router.push({ name: 'login' })
    }

    const goToRegister = () => {
        router.push({ name: 'register' })
    }

    return {
        handlePasswordResetRequest,
        goToLogin,
        goToRegister
    }
}
