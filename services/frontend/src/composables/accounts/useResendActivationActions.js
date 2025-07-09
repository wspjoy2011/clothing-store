import {useAccountStore} from '@/stores/accounts';
import {useNavigation} from '@/composables/accounts/useNavigation';
import {useNotifications} from '@/composables/accounts/useNotifications';

export function useResendActivationActions() {
    const accountStore = useAccountStore();
    const {goToRegister} = useNavigation();
    const {showSuccess, showError} = useNotifications();

    const handleResendActivation = async (email, formValid) => {
        if (!formValid.value) return;

        try {
            const result = await accountStore.resendActivation({email: email.value});

            if (result.success) {
                showSuccess(result.message || 'Activation email sent successfully!');
            } else {
                showError(result.message || 'Failed to send activation email');
            }
        } catch (error) {
            showError('An unexpected error occurred');
        }
    };

    return {
        handleResendActivation,
        goToRegister
    };
}
