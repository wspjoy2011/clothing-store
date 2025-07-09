import {ref, computed, onMounted} from 'vue';
import {useTheme} from 'vuetify';
import {useAccountStore} from '@/stores/accounts';
import {useNavigation} from '@/composables/accounts/useNavigation';

export function useLogoutPage() {
  const theme = useTheme();
  const accountStore = useAccountStore();
  const {goToHome, goToLogin} = useNavigation();

  const isDarkTheme = computed(() => theme.global.current.value.dark);

  const isLoading = ref(true);
  const logoutSuccess = ref(false);
  const logoutError = ref(null);
  const logoutWarning = ref(null);

  const performLogout = async () => {
    try {
      await new Promise(resolve => setTimeout(resolve, 1000));

      const result = await accountStore.logout();

      if (result.success) {
        logoutSuccess.value = true;

        if (result.warning) {
          logoutWarning.value = result.warning;
        }
      } else {
        logoutError.value = result.message || 'Failed to logout';
      }
    } catch (error) {
      logoutError.value = 'Network error occurred during logout';
      accountStore.clearLocalState();
    } finally {
      isLoading.value = false;
    }
  };

  onMounted(async () => {
    document.title = 'StyleShop - Logout';
    await performLogout();
  });

  return {
    isDarkTheme,
    isLoading,
    logoutSuccess,
    logoutError,
    logoutWarning,
    goToHome,
    goToLogin
  };
}
