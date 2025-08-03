import {ref, computed} from 'vue';
import {useCartStore} from '@/stores/cart.js';

export function useCartState() {
    const cartStore = useCartStore();

    const isAddingItem = ref(false);
    const addItemError = ref(null);

    const cart = computed(() => cartStore.cart);
    const isLoading = computed(() => cartStore.isLoading);
    const error = computed(() => cartStore.error);
    const hasItems = computed(() => cartStore.hasItems);
    const itemsCount = computed(() => cartStore.itemsCount);
    const totalPrice = computed(() => cartStore.totalPrice);
    const isAuthenticated = computed(() => cartStore.isAuthenticated);
    const isInitialized = computed(() => cartStore.isInitialized);

    const clearAddItemError = () => {
        addItemError.value = null;
    };

    const setAddingItem = (value) => {
        isAddingItem.value = value;
    };

    const setAddItemError = (error) => {
        addItemError.value = error;
    };

    return {
        // Local state
        isAddingItem,
        addItemError,

        // Cart state
        cart,
        isLoading,
        error,
        hasItems,
        itemsCount,
        totalPrice,
        isAuthenticated,
        isInitialized,

        // Actions
        clearAddItemError,
        setAddingItem,
        setAddItemError
    };
}
