import {ref, computed, watch, onMounted} from 'vue';
import {useTheme} from 'vuetify';
import {useAccountStore} from '@/stores/accounts';
import {useNavigation} from '@/composables/accounts/useNavigation';
import {useNotifications} from '@/composables/accounts/useNotifications';
import {useLoginAuth} from './useLoginAuth';

export function useLoginPage() {
  const theme = useTheme();
  const accountStore = useAccountStore();
  const {goToRegister, goToActivation, goToHome} = useNavigation();
  const notifications = useNotifications();
  const loginAuth = useLoginAuth();

  const facebookAppId = import.meta.env.VITE_FACEBOOK_APP_ID || '';
  const isDarkTheme = computed(() => theme.global.current.value.dark);

  const showSocialSuccessMessage = ref(false);
  const socialSuccessMessage = ref('');

  const formLoginError = ref('');
  const showFormLoginError = ref(false);

  const hideSocialSuccess = () => {
    showSocialSuccessMessage.value = false;
    socialSuccessMessage.value = '';
  };

  const showSocialSuccess = (message, authType) => {
    socialSuccessMessage.value = message;
    showSocialSuccessMessage.value = true;
    loginAuth.socialAuthType.value = authType;
  };

  const hideError = () => {
    notifications.hideError();
    accountStore.clearLoginState();
    clearFormLoginError();
  };

  const clearFormLoginError = () => {
    formLoginError.value = '';
    showFormLoginError.value = false;
  };

  const showFormLoginErrorMessage = (message) => {
    formLoginError.value = message;
    showFormLoginError.value = true;
  };

  const hideSuccess = () => {
    notifications.hideSuccess();
  };

  const hideWarning = () => {
    notifications.hideWarning();
  };

  watch(() => accountStore.hasLoginError, (hasError) => {
    if (hasError && accountStore.loginErrorMessage) {
      notifications.showError(accountStore.loginErrorMessage);
      showFormLoginErrorMessage(accountStore.loginErrorMessage);
    }
  });

  watch(() => accountStore.loginSuccess, (success) => {
    if (success) {
      notifications.showSuccess('Login successful! Welcome back.');
      setTimeout(() => {
        hideSuccess();
        goToHome();
      }, 1500);
    }
  });

  const handleEmailLogin = async (credentials) => {
    try {
      clearFormLoginError();

      const result = await loginAuth.handleEmailLogin(credentials);

      if (result && !result.success) {
        const errorMsg = result.error?.message || result.message || 'Login failed. Please try again.';
        notifications.showError(errorMsg);
        showFormLoginErrorMessage(errorMsg);
      }
    } catch (error) {
      const errorMsg = 'An unexpected error occurred. Please try again.';
      notifications.showError(errorMsg);
      showFormLoginErrorMessage(errorMsg);
    }
  };

  const handleGoogleLogin = async () => {
    const result = await loginAuth.handleGoogleLogin();

    if (result && result.success) {
      const message = result.isNewUser
        ? 'Welcome! Your Google account has been successfully registered and signed in.'
        : 'Welcome back! You have been signed in with your Google account.';

      showSocialSuccess(message, 'google');

      setTimeout(() => {
        hideSocialSuccess();
        goToHome();
      }, 3000);
    } else if (result && result.error) {
      notifications.showError(result.message || 'Google login failed. Please try again.');
    } else {
      notifications.showError('Google login failed. Please try again.');
    }
  };

  const handleFacebookSuccess = async (response) => {
    const result = await loginAuth.handleFacebookLogin(response);

    if (result && result.success) {
      const message = result.isNewUser
        ? 'Welcome! Your Facebook account has been successfully registered and signed in.'
        : 'Welcome back! You have been signed in with your Facebook account.';

      showSocialSuccess(message, 'facebook');

      setTimeout(() => {
        hideSocialSuccess();
        goToHome();
      }, 3000);
    } else if (result && result.error) {
      notifications.showError(result.message || 'Facebook login failed. Please try again.');
    } else {
      notifications.showError('Facebook login failed. Please try again.');
    }
  };

  const handleFacebookError = (error) => {
    const result = loginAuth.handleFacebookLoginError(error);
    if (result && result.error) {
      notifications.showError(result.message);
    }
  };

  const handleActivation = (email) => {
    goToActivation(email);
  };

  const handleRegistration = () => {
    goToRegister();
  };

  const handleRegisterClick = () => {
    goToRegister();
  };

  const handleClearLoginError = () => {
    clearFormLoginError();
    hideError();
  };

  onMounted(() => {
    document.title = 'StyleShop - Login';
    accountStore.clearLoginState();
    notifications.hideError();
    notifications.hideSuccess();
    notifications.hideWarning();
    clearFormLoginError();
  });

  return {
    isDarkTheme,
    facebookAppId,
    ...loginAuth,
    showSuccessMessage: notifications.showSuccessMessage,
    showErrorMessage: notifications.showErrorMessage,
    showWarningMessage: notifications.showWarningMessage,
    successMessage: notifications.successMessage,
    errorMessage: notifications.errorMessage,
    warningMessage: notifications.warningMessage,
    formLoginError,
    showFormLoginError,
    showSocialSuccessMessage,
    socialSuccessMessage,
    hideSocialSuccess,
    hideSuccess,
    hideError,
    hideWarning,
    handleEmailLogin,
    handleGoogleLogin,
    handleFacebookSuccess,
    handleFacebookError,
    handleActivation,
    handleRegistration,
    handleRegisterClick,
    handleClearLoginError
  };
}
