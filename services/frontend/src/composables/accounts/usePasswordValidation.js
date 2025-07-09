import {ref, computed} from 'vue';

export function usePasswordValidation() {
  const password = ref('');
  const confirmPassword = ref('');
  const passwordTouched = ref(false);
  const confirmPasswordTouched = ref(false);
  const showPassword = ref(false);
  const showConfirmPassword = ref(false);

  const passwordRules = [
    v => !!v || 'Password is required',
    v => v.length >= 8 || 'Password must be at least 8 characters',
    v => /(?=.*[a-z])/.test(v) || 'Password must contain at least one lowercase letter',
    v => /(?=.*[A-Z])/.test(v) || 'Password must contain at least one uppercase letter',
    v => /(?=.*\d)/.test(v) || 'Password must contain at least one number',
    v => /(?=.*[!@#$%^&*])/.test(v) || 'Password must contain at least one special character'
  ];

  const confirmPasswordRules = [
    v => !!v || 'Please confirm your password',
    v => v === password.value || 'Passwords do not match'
  ];

  const passwordError = computed(() => {
    if (!passwordTouched.value || !password.value) return false;
    return !passwordRules.every(rule => rule(password.value) === true);
  });

  const confirmPasswordError = computed(() => {
    if (!confirmPasswordTouched.value || !confirmPassword.value) return false;
    return !confirmPasswordRules.every(rule => rule(confirmPassword.value) === true);
  });

  const passwordErrorMessage = computed(() => {
    if (!passwordError.value) return '';
    const failedRule = passwordRules.find(rule => rule(password.value) !== true);
    return failedRule ? failedRule(password.value) : '';
  });

  const confirmPasswordErrorMessage = computed(() => {
    if (!confirmPasswordError.value) return '';
    const failedRule = confirmPasswordRules.find(rule => rule(confirmPassword.value) !== true);
    return failedRule ? failedRule(confirmPassword.value) : '';
  });

  const passwordFieldLabel = computed(() => {
    return (password.value && password.value.length > 0) ? 'Password (Strong)' : 'Password';
  });

  const isPasswordValid = computed(() => {
    return password.value && !passwordError.value;
  });

  const isConfirmPasswordValid = computed(() => {
    return confirmPassword.value && !confirmPasswordError.value;
  });

  const validatePassword = () => {
    passwordTouched.value = true;
    return isPasswordValid.value;
  };

  const validateConfirmPassword = () => {
    confirmPasswordTouched.value = true;
    return isConfirmPasswordValid.value;
  };

  const resetPasswordValidation = () => {
    password.value = '';
    confirmPassword.value = '';
    passwordTouched.value = false;
    confirmPasswordTouched.value = false;
    showPassword.value = false;
    showConfirmPassword.value = false;
  };

  return {
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
    isPasswordValid,
    isConfirmPasswordValid,
    validatePassword,
    validateConfirmPassword,
    resetPasswordValidation
  };
}
