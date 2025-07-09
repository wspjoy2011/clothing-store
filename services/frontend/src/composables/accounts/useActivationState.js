import {ref, computed} from 'vue';
import {useAccountStore} from '@/stores/accounts';

export function useActivationState() {
  const accountStore = useAccountStore();
  const activationAttempted = ref(false);

  const isLoading = computed(() => accountStore.isActivating);
  const activationSuccess = computed(() => accountStore.activationSuccess);
  const hasError = computed(() => accountStore.hasActivationError);
  const errorMessage = computed(() => accountStore.activationErrorMessage);
  const isTokenExpired = computed(() => accountStore.isTokenExpired);

  const clearActivationState = () => {
    activationAttempted.value = false;
    accountStore.clearActivationState();
  };

  const setActivationAttempted = (value) => {
    activationAttempted.value = value;
  };

  return {
    activationAttempted,
    isLoading,
    activationSuccess,
    hasError,
    errorMessage,
    isTokenExpired,
    clearActivationState,
    setActivationAttempted
  };
}
