import {useCartState} from '@/composables/cart/useCartState.js';
import {useCartActions} from '@/composables/cart/useCartActions.js';
import {useCartErrorHandler} from '@/composables/cart/useCartErrorHandler.js';
import {useCartItemChecker} from '@/composables/cart/useCartItemChecker.js';

export function useCart(options = {}) {
    const {
        showNotifications = true
    } = options;

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

    const {
        // Reactive methods for checking cart items
        isProductInCart,
        getCartItemInfo,
        getProductQuantity,
        getCartItemDisplayInfo,
        checkMultipleProducts,

        // Reactive properties
        cartProductIds,
        cartItemsMap,
        hasCartItems,
        totalItemsCount,

        // Synchronous methods
        checkProductInCartSync,
        getCartItemInfoSync,
        getProductQuantitySync
    } = useCartItemChecker();

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
        getCartErrorDetails,

        // Cart item checking (reactive)
        isProductInCart,
        getCartItemInfo,
        getProductQuantity,
        getCartItemDisplayInfo,
        checkMultipleProducts,
        cartProductIds,
        cartItemsMap,
        hasCartItems,
        totalItemsCount,

        // Cart item checking (synchronous)
        checkProductInCartSync,
        getCartItemInfoSync,
        getProductQuantitySync
    };
}
