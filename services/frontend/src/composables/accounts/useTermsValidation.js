import {ref, computed} from 'vue';
import {useLegalStore} from '@/stores/legal';

export function useTermsValidation() {
  const legalStore = useLegalStore();
  const acceptTerms = ref(false);
  const termsTouched = ref(false);

  const termsRules = [
    v => !!v || 'You must accept the terms and conditions'
  ];

  const termsError = computed(() => {
    if (!termsTouched.value) return false;
    return !acceptTerms.value;
  });

  const termsErrorMessage = computed(() => {
    if (!termsError.value) return '';
    return 'You must accept the terms and conditions';
  });

  const canAcceptTerms = computed(() => {
    return legalStore.hasReadBothDocuments;
  });

  const validateTerms = () => {
    termsTouched.value = true;
    return acceptTerms.value;
  };

  const resetTermsValidation = () => {
    acceptTerms.value = false;
    termsTouched.value = false;
  };

  const handleCheckboxClick = (event, showError) => {
    if (!canAcceptTerms.value) {
      event.preventDefault();
      event.stopPropagation();
      showError('Please read and accept both Terms of Service and Privacy Policy first');
      return false;
    }
    return true;
  };

  return {
    acceptTerms,
    termsTouched,
    termsRules,
    termsError,
    termsErrorMessage,
    canAcceptTerms,
    validateTerms,
    resetTermsValidation,
    handleCheckboxClick
  };
}
