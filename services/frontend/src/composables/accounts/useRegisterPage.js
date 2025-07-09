import {ref, computed} from 'vue';
import {useThemeState} from '@/composables/useThemeState';
import {usePageTitle} from '@/composables/usePageTitle';
import {useEmailValidation} from '@/composables/accounts/useEmailValidation';
import {usePasswordValidation} from '@/composables/accounts/usePasswordValidation';
import {useTermsValidation} from '@/composables/accounts/useTermsValidation';
import {useSocialAuthActions} from '@/composables/accounts/useSocialAuthActions';
import {useNotifications} from '@/composables/accounts/useNotifications';
import {useNavigation} from '@/composables/accounts/useNavigation';
import {useAccountStore} from '@/stores/accounts';
import {useLegalStore} from '@/stores/legal';

export function useRegisterPage() {
    const {isDarkTheme} = useThemeState();
    usePageTitle('StyleShop - Register');

    const accountStore = useAccountStore();
    const legalStore = useLegalStore();
    const facebookAppId = import.meta.env.VITE_FACEBOOK_APP_ID || '';

    const formRef = ref(null);
    const isFormValid = ref(false);

    const {
        email,
        emailRules,
        emailError,
        emailErrorMessage,
        emailTouched,
        validateEmail,
        resetEmailValidation
    } = useEmailValidation();

    const {
        password,
        confirmPassword,
        passwordTouched,
        confirmPasswordTouched,
        showPassword,
        showConfirmPassword,
        passwordRules,
        confirmPasswordRules,
        passwordError,
        confirmPasswordError,
        passwordErrorMessage,
        confirmPasswordErrorMessage,
        passwordFieldLabel,
        resetPasswordValidation
    } = usePasswordValidation();

    const {
        acceptTerms,
        termsRules,
        canAcceptTerms,
        handleCheckboxClick: baseHandleCheckboxClick,
        resetTermsValidation
    } = useTermsValidation();

    const {
        isSocialAuthLoading,
        socialAuthType,
        showSocialSuccessMessage,
        socialSuccessMessage,
        hideSocialSuccess,
        onGoogleRegister: baseOnGoogleRegister,
        onFacebookSuccess: baseOnFacebookSuccess,
        onFacebookError: baseOnFacebookError
    } = useSocialAuthActions();

    const {
        showSuccessMessage,
        showErrorMessage,
        errorMessage,
        successMessage,
        showSuccess,
        showError,
        hideSuccess,
        hideError
    } = useNotifications();

    const {
        goToLogin,
        goToHome,
        openTerms,
        openPrivacy,
        handleTermsAccept,
        handlePrivacyAcknowledge,
        HFaceBookLogin
    } = useNavigation();

    const isLoading = computed(() => accountStore.isRegistering);

    const isFormReady = computed(() => {
        const emailValid = email.value && /.+@.+\..+/.test(email.value);
        const passwordValid = password.value &&
            password.value.length >= 8 &&
            /(?=.*[a-z])/.test(password.value) &&
            /(?=.*[A-Z])/.test(password.value) &&
            /(?=.*\d)/.test(password.value) &&
            /(?=.*[!@#$%^&*])/.test(password.value);
        const confirmPasswordValid = confirmPassword.value && confirmPassword.value === password.value;
        const termsValid = acceptTerms.value;

        return emailValid && passwordValid && confirmPasswordValid && termsValid;
    });

    const resetForm = () => {
        resetEmailValidation();
        resetPasswordValidation();
        resetTermsValidation();
        isFormValid.value = false;

        accountStore.clearRegistrationState();

        if (formRef.value) {
            formRef.value.reset();
            formRef.value.resetValidation();
        }
    };

    const handleRegister = async () => {
        if (!formRef.value) return;

        try {
            accountStore.clearRegistrationState();

            const {valid} = await formRef.value.validate();
            if (!valid) return {success: false, error: 'Please fix validation errors'};

            const result = await accountStore.register({
                email: email.value,
                password: password.value
            });

            if (result.success) {
                return {success: true};
            } else {
                return {success: false, error: result.message};
            }
        } catch (error) {
            return {success: false, error: error.message || 'Registration failed. Please try again.'};
        }
    };

    const onRegister = async () => {
        const result = await handleRegister();

        if (result && result.success) {
            showSuccess('Account created successfully! Please check your email for verification.');
            resetForm();

            setTimeout(() => {
                hideSuccess();
                goToLogin();
            }, 4000);

        } else if (result && result.error) {
            showError(result.error);
        } else {
            showError('Registration failed. Please try again.');
        }
    };

    const handleCheckboxClick = (event) => {
        return baseHandleCheckboxClick(event, showError);
    };

    const onGoogleRegister = async () => {
        await baseOnGoogleRegister(showError);
    };

    const onFacebookSuccess = async (response) => {
        await baseOnFacebookSuccess(response, showError);
    };

    const onFacebookError = (error) => {
        baseOnFacebookError(error, showError);
    };

    return {
        isDarkTheme,
        facebookAppId,
        legalStore,
        formRef,
        isFormValid,
        email,
        password,
        confirmPassword,
        acceptTerms,
        showPassword,
        showConfirmPassword,
        isLoading,
        passwordFieldLabel,
        isFormReady,
        emailRules,
        passwordRules,
        confirmPasswordRules,
        termsRules,
        emailTouched,
        passwordTouched,
        confirmPasswordTouched,
        emailError,
        passwordError,
        confirmPasswordError,
        emailErrorMessage,
        passwordErrorMessage,
        confirmPasswordErrorMessage,
        canAcceptTerms,
        isSocialAuthLoading,
        socialAuthType,
        showSocialSuccessMessage,
        socialSuccessMessage,
        showSuccessMessage,
        showErrorMessage,
        errorMessage,
        successMessage,
        resetForm,
        onRegister,
        handleCheckboxClick,
        hideSocialSuccess,
        onGoogleRegister,
        onFacebookSuccess,
        onFacebookError,
        hideSuccess,
        hideError,
        goToLogin,
        goToHome,
        openTerms,
        openPrivacy,
        handleTermsAccept,
        handlePrivacyAcknowledge,
        HFaceBookLogin
    };
}
