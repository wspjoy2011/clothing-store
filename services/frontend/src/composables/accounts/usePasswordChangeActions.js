import { useAccountStore } from '@/stores/accounts'

export function usePasswordChangeActions() {
    const accountStore = useAccountStore()

    const handlePasswordChange = async (oldPassword, newPassword, formValid, { setChangeError, setChangeSuccess, setChanging }) => {
        if (!formValid.value) {
            setChangeError('Please fill in all fields correctly')
            return
        }

        if (!accountStore.accessToken) {
            setChangeError('You must be logged in to change your password')
            return
        }

        setChanging(true)

        try {
            await accountStore.changePassword({
                old_password: oldPassword.value,
                new_password: newPassword.value
            })

            setChangeSuccess()
        } catch (error) {
            const errorMessage = error.message ||
                              error.response?.data?.detail ||
                              'Password change failed. Please try again.'
            setChangeError(errorMessage)
        } finally {
            setChanging(false)
        }
    }

    return {
        handlePasswordChange
    }
}
