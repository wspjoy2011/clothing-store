import {ref, computed, onMounted, onUnmounted} from 'vue';
import {useAccountStore} from '@/stores/accounts';

export function useResendActivationState() {
    const accountStore = useAccountStore();
    const formValid = ref(false);
    const resendForm = ref(null);

    const isResending = computed(() => accountStore.isResending);
    const hasResendError = computed(() => accountStore.hasResendError);
    const resendErrorMessage = computed(() => accountStore.resendErrorMessage);
    const resendSuccess = computed(() => accountStore.resendSuccess);

    const clearResendState = () => {
        accountStore.clearResendState();
    };

    const resetForm = () => {
        clearResendState();
        formValid.value = false;
        if (resendForm.value) {
            resendForm.value.resetValidation();
        }
    };

    onMounted(() => {
        clearResendState();
    });

    onUnmounted(() => {
        clearResendState();
    });

    return {
        formValid,
        resendForm,
        isResending,
        hasResendError,
        resendErrorMessage,
        resendSuccess,
        clearResendState,
        resetForm
    };
}
