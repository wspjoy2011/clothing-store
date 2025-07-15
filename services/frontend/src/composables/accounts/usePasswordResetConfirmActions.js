import { useRouter } from 'vue-router'
import { useAccountStore } from '@/stores/accounts'
import { useNotifications } from '@/composables/accounts/useNotifications'

export function usePasswordResetConfirmActions() {
    const router = useRouter()
    const accountStore = useAccountStore()
    const { showSuccess, showError } = useNotifications()

    const handlePasswordResetConfirm = async (token, password, formValid, { setConfirmError, setConfirmSuccess, setConfirming }) => {
        if (!formValid.value) return

        setConfirming(true)

        try {
            const result = await accountStore.confirmPasswordReset({
                token: token.value,
                new_password: password.value
            })

            if (result.success) {
                setConfirmSuccess()
                showSuccess('Password reset successful! You can now login with your new password.')

                setTimeout(() => {
                    router.push({ name: 'login' })
                }, 3000)
            } else {
                setConfirmError(result.message || 'Failed to reset password')
                showError(result.message || 'Failed to reset password')
            }
        } catch (error) {
            setConfirmError('An unexpected error occurred')
            showError('An unexpected error occurred')
        } finally {
            setConfirming(false)
        }
    }

    const goToLogin = () => {
        router.push({ name: 'login' })
    }

    const goToPasswordReset = () => {
        router.push({ name: 'password-reset-request' })
    }

    const goToRegister = () => {
        router.push({ name: 'register' })
    }

    return {
        handlePasswordResetConfirm,
        goToLogin,
        goToPasswordReset,
        goToRegister
    }
}
