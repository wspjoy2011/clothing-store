import {ref, computed} from 'vue';

export function useLoginForm() {
    const formRef = ref(null);
    const isFormValid = ref(false);
    const email = ref('');
    const password = ref('');
    const showPassword = ref(false);
    const emailTouched = ref(false);
    const passwordTouched = ref(false);
    const hasLoginError = ref(false);
    const loginErrorMessage = ref('');

    const emailRules = [
        v => !!v || 'Email is required',
        v => /.+@.+\..+/.test(v) || 'Email must be valid'
    ];

    const passwordRules = [
        v => !!v || 'Password is required',
        v => v.length >= 8 || 'Password must be at least 8 characters'
    ];

    const emailError = computed(() => {
        if (!emailTouched.value || !email.value) return false;
        return !emailRules.every(rule => rule(email.value) === true);
    });

    const emailErrorMessage = computed(() => {
        if (!emailError.value) return '';
        const failedRule = emailRules.find(rule => rule(email.value) !== true);
        return failedRule ? failedRule(email.value) : '';
    });

    const passwordError = computed(() => {
        if (!passwordTouched.value || !password.value) return false;
        return !passwordRules.every(rule => rule(password.value) === true);
    });

    const passwordErrorMessage = computed(() => {
        if (!passwordError.value) return '';
        const failedRule = passwordRules.find(rule => rule(password.value) !== true);
        return failedRule ? failedRule(password.value) : '';
    });

    const emailHasError = computed(() => {
        return emailError.value || (hasLoginError.value && emailTouched.value);
    });

    const passwordHasError = computed(() => {
        return passwordError.value || (hasLoginError.value && passwordTouched.value);
    });

    const emailDisplayErrorMessage = computed(() => {
        if (emailError.value) {
            return emailErrorMessage.value;
        }
        if (hasLoginError.value && emailTouched.value) {
            return loginErrorMessage.value;
        }
        return '';
    });

    const passwordDisplayErrorMessage = computed(() => {
        if (passwordError.value) {
            return passwordErrorMessage.value;
        }
        if (hasLoginError.value && passwordTouched.value) {
            return loginErrorMessage.value;
        }
        return '';
    });

    const isFormReady = computed(() => {
        return isFormValid.value &&
            email.value &&
            password.value &&
            !emailError.value &&
            !passwordError.value;
    });

    const setLoginError = (errorMessage) => {
        hasLoginError.value = true;
        loginErrorMessage.value = errorMessage;
    };

    const clearLoginError = () => {
        hasLoginError.value = false;
        loginErrorMessage.value = '';
    };

    const resetForm = () => {
        email.value = '';
        password.value = '';
        emailTouched.value = false;
        passwordTouched.value = false;
        clearLoginError();

        if (formRef.value) {
            formRef.value.reset();
            formRef.value.resetValidation();
        }
    };

    return {
        formRef,
        isFormValid,
        email,
        password,
        showPassword,
        emailTouched,
        passwordTouched,
        emailRules,
        passwordRules,
        emailError,
        emailErrorMessage,
        passwordError,
        passwordErrorMessage,
        emailHasError,
        passwordHasError,
        emailDisplayErrorMessage,
        passwordDisplayErrorMessage,
        isFormReady,
        hasLoginError,
        loginErrorMessage,
        setLoginError,
        clearLoginError,
        resetForm
    };
}
