import {computed} from 'vue';
import {useAccountStore} from '@/stores/accounts';

export function useActivationErrorHandler() {
  const accountStore = useAccountStore();

  const getErrorDetails = computed(() => {
    const status = accountStore.activationError?.status;

    const errorMap = {
      410: {
        icon: 'mdi-clock-alert',
        title: 'Link Expired',
        canRetry: false,
        showResend: true,
        showRegister: false
      },
      404: {
        icon: 'mdi-account-question',
        title: 'User Not Found',
        canRetry: false,
        showResend: false,
        showRegister: true
      },
      400: {
        icon: 'mdi-shield-alert',
        title: 'Invalid Request',
        canRetry: false,
        showResend: false,
        showRegister: false
      },
      500: {
        icon: 'mdi-alert-circle',
        title: 'Activation Failed',
        canRetry: true,
        showResend: false,
        showRegister: false
      }
    };

    return errorMap[status] || {
      icon: 'mdi-alert-circle',
      title: 'Activation Failed',
      canRetry: false,
      showResend: false,
      showRegister: false
    };
  });

  return {
    getErrorDetails
  };
}
