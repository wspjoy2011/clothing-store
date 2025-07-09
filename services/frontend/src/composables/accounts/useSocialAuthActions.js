import {ref} from 'vue';
import {useNavigation} from '@/composables/accounts/useNavigation';

export function useSocialAuthActions() {
    const {handleGoogleAuth, handleFacebookSuccess, handleFacebookError, goToHome} = useNavigation();

    const isSocialAuthLoading = ref(false);
    const socialAuthType = ref('');
    const showSocialSuccessMessage = ref(false);
    const socialSuccessMessage = ref('');

    const hideSocialSuccess = () => {
        showSocialSuccessMessage.value = false;
        socialSuccessMessage.value = '';
        socialAuthType.value = '';
    };

    const showSocialSuccess = (message, type) => {
        socialSuccessMessage.value = message;
        socialAuthType.value = type;
        showSocialSuccessMessage.value = true;
    };

    const onGoogleRegister = async (showError) => {
        isSocialAuthLoading.value = true;
        socialAuthType.value = 'google';

        try {
            const result = await handleGoogleAuth(false);

            if (result && result.success) {
                const message = result.isNewUser
                    ? 'Welcome! Your Google account has been successfully registered.'
                    : 'Welcome back! You have been signed in with your existing Google account.';

                showSocialSuccess(message, 'google');

                setTimeout(() => {
                    hideSocialSuccess();
                    goToHome();
                }, 4000);

            } else if (result && result.error) {
                showError(result.message || 'Google registration failed. Please try again.');
            } else {
                showError('Google registration failed. Please try again.');
            }

        } catch (error) {
            console.error('Google registration error:', error);
            showError('An unexpected error occurred during Google registration.');
        } finally {
            isSocialAuthLoading.value = false;
            socialAuthType.value = '';
        }
    };

    const onFacebookSuccess = async (response, showError) => {
        isSocialAuthLoading.value = true;
        socialAuthType.value = 'facebook';

        try {
            const result = await handleFacebookSuccess(response);

            if (result && result.success) {
                const message = result.isNewUser
                    ? 'Welcome! Your Facebook account has been successfully registered.'
                    : 'Welcome back! You have been signed in with your existing Facebook account.';

                showSocialSuccess(message, 'facebook');

                setTimeout(() => {
                    hideSocialSuccess();
                    goToHome();
                }, 4000);

            } else if (result && result.error) {
                showError(result.message || 'Facebook registration failed. Please try again.');
            } else {
                showError('Facebook registration failed. Please try again.');
            }

        } catch (error) {
            console.error('Facebook registration error:', error);
            showError('An unexpected error occurred during Facebook registration.');
        } finally {
            isSocialAuthLoading.value = false;
            socialAuthType.value = '';
        }
    };

    const onFacebookError = (error, showError) => {
        const result = handleFacebookError(error);
        if (result && result.error) {
            showError(result.message || 'Facebook registration failed. Please try again.');
        } else {
            showError('Facebook registration failed. Please try again.');
        }
    };

    return {
        isSocialAuthLoading,
        socialAuthType,
        showSocialSuccessMessage,
        socialSuccessMessage,
        hideSocialSuccess,
        showSocialSuccess,
        onGoogleRegister,
        onFacebookSuccess,
        onFacebookError
    };
}
