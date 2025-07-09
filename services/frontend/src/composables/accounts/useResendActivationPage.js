import {useThemeState} from '@/composables/useThemeState';
import {usePageTitle} from '@/composables/usePageTitle';
import {useEmailValidation} from '@/composables/accounts/useEmailValidation';
import {useResendActivationState} from '@/composables/accounts/useResendActivationState';
import {useResendActivationActions} from '@/composables/accounts/useResendActivationActions';

export function useResendActivationPage(props) {
    const {isDarkTheme} = useThemeState();
    usePageTitle('StyleShop - Resend Activation');

    const {
        email,
        emailRules,
        resetEmailValidation
    } = useEmailValidation();

    const {
        formValid,
        resendForm,
        isResending,
        hasResendError,
        resendErrorMessage,
        resendSuccess,
        resetForm: baseResetForm
    } = useResendActivationState();

    const {
        handleResendActivation: baseHandleResendActivation,
        goToRegister
    } = useResendActivationActions();

    // Initialize email from props
    if (props.email) {
        email.value = props.email;
    }

    const handleResendActivation = async () => {
        await baseHandleResendActivation(email, formValid);
    };

    const resetForm = () => {
        baseResetForm();
        resetEmailValidation();
    };

    return {
        isDarkTheme,
        email,
        emailRules,
        formValid,
        resendForm,
        isResending,
        hasResendError,
        resendErrorMessage,
        resendSuccess,
        handleResendActivation,
        resetForm,
        goToRegister
    };
}
