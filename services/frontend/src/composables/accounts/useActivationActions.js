import {computed} from 'vue';
import {useAccountStore} from '@/stores/accounts';
import {useNavigation} from '@/composables/accounts/useNavigation';

export function useActivationActions(props) {
    const accountStore = useAccountStore();
    const {goToLogin, goToRegister, goToHome, goToResendActivation} = useNavigation();

    const hasValidParams = computed(() => {
        return props.email && props.token;
    });

    const activateAccount = async (activationAttempted) => {
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

    const retryActivation = async (activationAttempted, clearActivationState) => {
        activationAttempted.value = false;
        clearActivationState();
        await activateAccount(activationAttempted);
    };

    const handleResendActivation = () => {
        goToResendActivation(props.email);
    };

    return {
        hasValidParams,
        activateAccount,
        retryActivation,
        handleResendActivation,
        goToLogin,
        goToRegister,
        goToHome
    };
}
