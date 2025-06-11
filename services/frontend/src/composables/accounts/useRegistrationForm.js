import { ref, computed, watch, nextTick } from 'vue'

import { useAccountStore } from '@/stores/accounts'
import { useFormValidation } from './useFormValidation'

export function useRegistrationForm() {
  const accountStore = useAccountStore()
  const validation = useFormValidation()

  const formRef = ref(null)
  const isFormValid = ref(false)
  const email = ref('')
  const password = ref('')
  const confirmPassword = ref('')
  const acceptTerms = ref(false)
  const showPassword = ref(false)
  const showConfirmPassword = ref(false)

  const isLoading = computed(() => accountStore.isRegistering)
  const emailServerError = computed(() => accountStore.isEmailAlreadyExists)

  const passwordFieldLabel = computed(() => {
    return (password.value && password.value.length > 0) ? 'Password (Strong)' : 'Password'
  })

  const isFormReady = computed(() => {
    const emailValid = email.value && /.+@.+\..+/.test(email.value)
    const passwordValid = password.value &&
      password.value.length >= 8 &&
      /(?=.*[a-z])/.test(password.value) &&
      /(?=.*[A-Z])/.test(password.value) &&
      /(?=.*\d)/.test(password.value) &&
      /(?=.*[!@#$%^&*])/.test(password.value)
    const confirmPasswordValid = confirmPassword.value && confirmPassword.value === password.value
    const termsValid = acceptTerms.value

    return emailValid && passwordValid && confirmPasswordValid && termsValid
  })

  const emailRules = [
    v => validation.validateEmail(v, emailServerError.value)
  ]

  const passwordRules = [
    v => validation.validatePassword(v)
  ]

  const confirmPasswordRules = [
    v => validation.validateConfirmPassword(v, password.value)
  ]

  const termsRules = [
    v => !!v || 'You must accept the terms and conditions'
  ]

  const resetForm = () => {
    email.value = ''
    password.value = ''
    confirmPassword.value = ''
    acceptTerms.value = false

    validation.resetValidationState()
    accountStore.clearRegistrationState()

    if (formRef.value) {
      formRef.value.reset()
      formRef.value.resetValidation()
    }
  }

  watch(password, () => {
    if (validation.confirmPasswordTouched.value) {
      validation.validateConfirmPassword(confirmPassword.value, password.value)
    }
  })

  watch(email, (newVal) => {
    if (newVal !== undefined) {
      if (emailServerError.value) {
        accountStore.clearRegistrationState()
      }
      validation.validateEmail(newVal, emailServerError.value)
    }
  })

  watch(password, (newVal) => {
    if (newVal !== undefined) {
      validation.validatePassword(newVal)
    }
  })

  watch(confirmPassword, (newVal) => {
    if (newVal !== undefined) {
      validation.validateConfirmPassword(newVal, password.value)
    }
  })

  const handleRegister = async () => {
    if (!formRef.value) return

    try {
      accountStore.clearRegistrationState()
      validation.markAllTouched()

      const { valid } = await formRef.value.validate()
      if (!valid) return { success: false, error: 'Please fix validation errors' }

      const result = await accountStore.register({
        email: email.value,
        password: password.value
      })

      if (result.success) {
        return { success: true }
      } else {
        if (result.error?.status === 409) {
          await nextTick()
          if (formRef.value) {
            formRef.value.validate()
          }
        }
        return { success: false, error: result.message }
      }
    } catch (error) {
      console.error('Registration error:', error)
      return { success: false, error: error.message || 'Registration failed. Please try again.' }
    }
  }

  return {
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
    resetForm,
    handleRegister,
    ...validation
  }
}
