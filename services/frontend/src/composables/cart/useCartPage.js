import {onMounted} from 'vue';
import {useCartState} from '@/composables/cart/useCartState.js';
import {useCartActions} from '@/composables/cart/useCartActions.js';
import {useCartErrorHandler} from '@/composables/cart/useCartErrorHandler.js';
import {usePageTitle} from '@/composables/usePageTitle.js';

export function useCartPage(options = {}) {
    const {
        autoInitialize = true,
        showNotifications = true
    } = options;

    usePageTitle('StyleShop - Shopping Cart');

    const {
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

        // State actions
        clearAddItemError,
        setAddingItem,
        setAddItemError
    } = useCartState();

    const {
        initializeCart,
        addItemToCart: baseAddItemToCart,
        reloadCart,
        switchToUserCart,
        switchToAnonymousCart
    } = useCartActions();

    const {
        getAddItemErrorDetails,
        getCartErrorDetails
    } = useCartErrorHandler();

    const addItemToCart = async (itemData) => {
        if (isAddingItem.value) return;

        setAddingItem(true);
        clearAddItemError();

        try {
            return await baseAddItemToCart(itemData, showNotifications);
        } catch (error) {
            setAddItemError(error.message);
            throw error;
        } finally {
            setAddingItem(false);
        }
    };

    if (autoInitialize) {
        onMounted(async () => {
            if (!isInitialized.value) {
                await initializeCart();
            }
        });
    }

    return {
        // State
        cart,
        isLoading,
        error,
        hasItems,
        itemsCount,
        totalPrice,
        isAuthenticated,
        isInitialized,

        // Add item state
        isAddingItem,
        addItemError,

        // Actions
        initializeCart,
        addItemToCart,
        reloadCart,
        switchToUserCart,
        switchToAnonymousCart,
        clearAddItemError,

        // Error handling
        getAddItemErrorDetails,
        getCartErrorDetails
    };
}
