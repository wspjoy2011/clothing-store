import {watchEffect} from 'vue';
import {useThemeState} from '@/composables/useThemeState';
import {useActivationState} from '@/composables/accounts/useActivationState';
import {useActivationErrorHandler} from '@/composables/accounts/useActivationErrorHandler';
import {useActivationActions} from '@/composables/accounts/useActivationActions';
import {usePageTitle} from '@/composables/usePageTitle';

export function useActivationPage(props) {
  const {isDarkTheme} = useThemeState();
  usePageTitle('StyleShop - Activate Account');

  const {
    activationAttempted,
    isLoading,
    activationSuccess,
    hasError,
    errorMessage,
    isTokenExpired,
    clearActivationState,
    setActivationAttempted
  } = useActivationState();

  const {getErrorDetails} = useActivationErrorHandler();

  const {
    hasValidParams,
    activateAccount,
    retryActivation: baseRetryActivation,
    handleResendActivation,
    goToLogin,
    goToRegister,
    goToHome
  } = useActivationActions(props);

  const retryActivation = async () => {
    await baseRetryActivation(activationAttempted, clearActivationState);
  };

  watchEffect(() => {
    if (hasValidParams.value && !activationAttempted.value) {
      clearActivationState();
      activateAccount(activationAttempted);
    }
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
