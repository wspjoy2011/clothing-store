import {useRouter} from 'vue-router'
import {useThemeState} from '@/composables/useThemeState'
import {usePageTitle} from '@/composables/usePageTitle'
import {usePasswordChangeValidation} from '@/composables/accounts/usePasswordChangeValidation'
import {usePasswordChangeState} from '@/composables/accounts/usePasswordChangeState'
import {usePasswordChangeActions} from '@/composables/accounts/usePasswordChangeActions'
import {useAccountStore} from '@/stores/accounts'

export function usePasswordChangePage() {
    const router = useRouter()
    const {isDarkTheme} = useThemeState()
    const accountStore = useAccountStore()
    usePageTitle('StyleShop - Change Password')

    const {
        oldPassword,
        newPassword,
        confirmPassword,
        showOldPassword,
        showNewPassword,
        showConfirmPassword,
        oldPasswordRules,
        newPasswordRules,
        confirmPasswordRules,
        resetPasswordChangeValidation
    } = usePasswordChangeValidation()

    const {
        formValid,
        changeFormRef,
        isChanging,
        hasChangeError,
        changeErrorMessage,
        changeSuccess,
        resetForm: baseResetForm,
        setChangeError,
        setChangeSuccess,
        setChanging
    } = usePasswordChangeState()

    const {
        handlePasswordChange: baseHandlePasswordChange
    } = usePasswordChangeActions()

    const handlePasswordChange = async () => {
        await baseHandlePasswordChange(oldPassword, newPassword, formValid, {
            setChangeError,
            setChangeSuccess,
            setChanging
        })
    }

    const resetForm = () => {
        baseResetForm()
        resetPasswordChangeValidation()
    }

    const goToProfile = () => {
        router.push({name: 'profile'})
    }

    const goToHome = () => {
        router.push({name: 'home'})
    }

    return {
        isDarkTheme,
        userEmail: accountStore.userEmail,
        oldPassword,
        newPassword,
        confirmPassword,
        showOldPassword,
        showNewPassword,
        showConfirmPassword,
        oldPasswordRules,
        newPasswordRules,
        confirmPasswordRules,
        formValid,
        changeForm: changeFormRef,
        isChanging,
        hasChangeError,
        changeErrorMessage,
        changeSuccess,
        handlePasswordChange,
        resetForm,
        goToProfile,
        goToHome
    }
}
