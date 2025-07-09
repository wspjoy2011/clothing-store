import {ref, computed, onMounted, watchEffect} from 'vue';
import {useTheme} from 'vuetify';
import {useAccountStore} from '@/stores/accounts';
import {useNavigation} from '@/composables/accounts/useNavigation';

export function useActivationPage(props) {
  const theme = useTheme();
  const accountStore = useAccountStore();
  const {goToLogin, goToRegister, goToHome, goToResendActivation} = useNavigation();

  const activationAttempted = ref(false);
  const isDarkTheme = computed(() => theme.global.current.value.dark);

  const hasValidParams = computed(() => {
    return props.email && props.token;
  });

  const isLoading = computed(() => accountStore.isActivating);
  const activationSuccess = computed(() => accountStore.activationSuccess);
  const hasError = computed(() => accountStore.hasActivationError);
  const errorMessage = computed(() => accountStore.activationErrorMessage);
  const isTokenExpired = computed(() => accountStore.isTokenExpired);

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
        canRetry: hasValidParams.value,
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

  const activateAccount = async () => {
    if (!hasValidParams.value || activationAttempted.value) {
      return;
    }

    activationAttempted.value = true;

    const result = await accountStore.activate({
      email: props.email,
      token: props.token
    });

    return result;
  };

  const retryActivation = async () => {
    activationAttempted.value = false;
    accountStore.clearActivationState();
    await activateAccount();
  };

  const handleResendActivation = () => {
    goToResendActivation(props.email);
  };

  watchEffect(() => {
    if (hasValidParams.value && !activationAttempted.value) {
      accountStore.clearActivationState();
      activateAccount();
    }
  });

  onMounted(() => {
    document.title = 'StyleShop - Activate Account';
    accountStore.clearActivationState();
  });

  return {
    isDarkTheme,
    isLoading,
    activationSuccess,
    hasError,
    errorMessage,
    isTokenExpired,
    hasValidParams,
    getErrorDetails,
    retryActivation,
    handleResendActivation,
    goToLogin,
    goToRegister,
    goToHome
  };
}
