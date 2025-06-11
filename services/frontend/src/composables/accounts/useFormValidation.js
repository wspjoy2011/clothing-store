import {ref} from 'vue'

export function useFormValidation() {
    const emailTouched = ref(false)
    const passwordTouched = ref(false)
    const confirmPasswordTouched = ref(false)

    const emailError = ref(false)
    const passwordError = ref(false)
    const confirmPasswordError = ref(false)
    const emailErrorMessage = ref('')
    const passwordErrorMessage = ref('')
    const confirmPasswordErrorMessage = ref('')

    const validateEmail = (value, serverError = false) => {
        if (!value) {
            emailError.value = emailTouched.value
            emailErrorMessage.value = emailTouched.value ? 'Email is required' : ''
            return emailTouched.value ? 'Email is required' : true
        }
        if (!/.+@.+\..+/.test(value)) {
            emailError.value = emailTouched.value
            emailErrorMessage.value = emailTouched.value ? 'Email must be valid' : ''
            return emailTouched.value ? 'Email must be valid' : true
        }

        if (serverError) {
            emailError.value = true
            emailErrorMessage.value = 'This email is already registered. Please use a different email.'
            return 'This email is already registered. Please use a different email.'
        }

        emailError.value = false
        emailErrorMessage.value = ''
        return true
    }

    const validatePassword = (value) => {
        if (!value) {
            passwordError.value = passwordTouched.value
            passwordErrorMessage.value = passwordTouched.value ? 'Password is required' : ''
            return passwordTouched.value ? 'Password is required' : true
        }
        if (value.length < 8) {
            passwordError.value = passwordTouched.value
            passwordErrorMessage.value = passwordTouched.value ? 'Password must be at least 8 characters' : ''
            return passwordTouched.value ? 'Password must be at least 8 characters' : true
        }
        if (!/(?=.*[a-z])/.test(value)) {
            passwordError.value = passwordTouched.value
            passwordErrorMessage.value = passwordTouched.value ? 'Password must contain at least one lowercase letter' : ''
            return passwordTouched.value ? 'Password must contain at least one lowercase letter' : true
        }
        if (!/(?=.*[A-Z])/.test(value)) {
            passwordError.value = passwordTouched.value
            passwordErrorMessage.value = passwordTouched.value ? 'Password must contain at least one uppercase letter' : ''
            return passwordTouched.value ? 'Password must contain at least one uppercase letter' : true
        }
        if (!/(?=.*\d)/.test(value)) {
            passwordError.value = passwordTouched.value
            passwordErrorMessage.value = passwordTouched.value ? 'Password must contain at least one number' : ''
            return passwordTouched.value ? 'Password must contain at least one number' : true
        }
        if (!/(?=.*[!@#$%^&*])/.test(value)) {
            passwordError.value = passwordTouched.value
            passwordErrorMessage.value = passwordTouched.value ? 'Password must contain at least one special character' : ''
            return passwordTouched.value ? 'Password must contain at least one special character' : true
        }
        passwordError.value = false
        passwordErrorMessage.value = ''
        return true
    }

    const validateConfirmPassword = (value, originalPassword) => {
        if (!value) {
            confirmPasswordError.value = confirmPasswordTouched.value
            confirmPasswordErrorMessage.value = confirmPasswordTouched.value ? 'Please confirm your password' : ''
            return confirmPasswordTouched.value ? 'Please confirm your password' : true
        }
        if (value !== originalPassword) {
            confirmPasswordError.value = confirmPasswordTouched.value
            confirmPasswordErrorMessage.value = confirmPasswordTouched.value ? 'Passwords do not match' : ''
            return confirmPasswordTouched.value ? 'Passwords do not match' : true
        }
        confirmPasswordError.value = false
        confirmPasswordErrorMessage.value = ''
        return true
    }

    const resetValidationState = () => {
        emailTouched.value = false
        passwordTouched.value = false
        confirmPasswordTouched.value = false
        emailError.value = false
        passwordError.value = false
        confirmPasswordError.value = false
        emailErrorMessage.value = ''
        passwordErrorMessage.value = ''
        confirmPasswordErrorMessage.value = ''
    }

    const markAllTouched = () => {
        emailTouched.value = true
        passwordTouched.value = true
        confirmPasswordTouched.value = true
    }

    return {
        emailTouched,
        passwordTouched,
        confirmPasswordTouched,
        emailError,
        passwordError,
        confirmPasswordError,
        emailErrorMessage,
        passwordErrorMessage,
        confirmPasswordErrorMessage,
        validateEmail,
        validatePassword,
        validateConfirmPassword,
        resetValidationState,
        markAllTouched
    }
}
