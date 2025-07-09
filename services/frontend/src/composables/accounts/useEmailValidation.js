import {ref, computed} from 'vue';

export function useEmailValidation() {
  const email = ref('');
  const emailTouched = ref(false);

  const emailRules = [
    v => !!v || 'Email is required',
    v => /.+@.+\..+/.test(v) || 'Email must be valid'
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

  const isEmailValid = computed(() => {
    return email.value && !emailError.value;
  });

  const validateEmail = () => {
    emailTouched.value = true;
    return isEmailValid.value;
  };

  const resetEmailValidation = () => {
    email.value = '';
    emailTouched.value = false;
  };

  return {
    email,
    emailTouched,
    emailRules,
    emailError,
    emailErrorMessage,
    isEmailValid,
    validateEmail,
    resetEmailValidation
  };
}
