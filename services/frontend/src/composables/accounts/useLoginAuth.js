import {computed, ref} from 'vue';
import {useAccountStore} from '@/stores/accounts';
import {useNavigation} from '@/composables/accounts/useNavigation';

export function useLoginAuth() {
    const accountStore = useAccountStore();
    const {handleGoogleAuth, handleFacebookSuccess, handleFacebookError, goToHome} = useNavigation();

    const isSocialAuthLoading = ref(false);
    const socialAuthType = ref('');

    const isLoading = computed(() => accountStore.isLoggingIn);
    const needsActivation = computed(() => accountStore.needsActivation);
    const needsRegistration = computed(() => accountStore.needsRegistration);

    const showActionButtons = computed(() => {
        return accountStore.hasLoginError && (needsActivation.value || needsRegistration.value);
    });

    const handleEmailLogin = async (credentials) => {
        try {
            accountStore.clearLoginState();

            const result = await accountStore.login({
                email: credentials.email,
                password: credentials.password
            });

            if (!result.success) {
                return result;
            }

            return result;
        } catch (error) {
            return {
                success: false,
                error: {message: 'An unexpected error occurred during login.'}
            };
        }
    };

    const handleGoogleLogin = async () => {
        isSocialAuthLoading.value = true;
        socialAuthType.value = 'google';

        try {
            return await handleGoogleAuth(true);
        } catch (error) {
            return {
                success: false,
                error: {message: 'An unexpected error occurred during Google login.'}
            };
        } finally {
            isSocialAuthLoading.value = false;
            socialAuthType.value = '';
        }
    };

    const handleFacebookLogin = async (response) => {
        isSocialAuthLoading.value = true;
        socialAuthType.value = 'facebook';

        try {
            return await handleFacebookSuccess(response);
        } catch (error) {
            return {
                success: false,
                error: {message: 'An unexpected error occurred during Facebook login.'}
            };
        } finally {
            isSocialAuthLoading.value = false;
            socialAuthType.value = '';
        }
    };

    const handleFacebookLoginError = (error) => {
        return handleFacebookError(error);
    };

    return {
        isLoading,
        isSocialAuthLoading,
        socialAuthType,
        needsActivation,
        needsRegistration,
        showActionButtons,
        handleEmailLogin,
        handleGoogleLogin,
        handleFacebookLogin,
        handleFacebookLoginError
    };
}
