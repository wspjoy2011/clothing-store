import {useEmailValidation} from '@/composables/accounts/useEmailValidation'
import {usePasswordResetRequestState} from '@/composables/accounts/usePasswordResetRequestState'
import {usePasswordResetRequestActions} from '@/composables/accounts/usePasswordResetRequestActions'
import {useThemeState} from '@/composables/useThemeState'
import {usePageTitle} from '@/composables/usePageTitle'

export function usePasswordResetRequestPage(props) {
    const {isDarkTheme} = useThemeState()
    usePageTitle('StyleShop - Reset Password')

    const {
        email,
        emailRules,
        resetEmailValidation
    } = useEmailValidation()

    const {
        formValid,
        resetFormRef,
        isRequesting,
        hasRequestError,
        requestErrorMessage,
        requestSuccess,
        resetForm: baseResetForm,
        setRequestError,
        setRequestSuccess,
        setRequesting
    } = usePasswordResetRequestState()

    const {
        handlePasswordResetRequest: baseHandlePasswordResetRequest,
        goToLogin,
        goToRegister
    } = usePasswordResetRequestActions()

    if (props.email) {
        email.value = props.email
    }

    const handlePasswordResetRequest = async () => {
        await baseHandlePasswordResetRequest(email, formValid, {
            setRequestError,
            setRequestSuccess,
            setRequesting
        })
    }

    const resetFormData = () => {
        baseResetForm()
        resetEmailValidation()
    }

    return {
        isDarkTheme,
        email,
        emailRules,
        formValid,
        resetForm: resetFormRef,
        isRequesting,
        hasRequestError,
        requestErrorMessage,
        requestSuccess,
        handlePasswordResetRequest,
        resetFormData,
        goToLogin,
        goToRegister
    }
}
