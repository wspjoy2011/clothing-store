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
        isRemovingItem,
        removeItemError,

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
        setAddItemError,
        clearRemoveItemError,
        setRemovingItem,
        setRemoveItemError
    } = useCartState();

    const {
        initializeCart,
        createAddItemHandler,
        createRemoveItemHandler,
        reloadCart,
        switchToUserCart,
        switchToAnonymousCart
    } = useCartActions();

    const {
        getAddItemErrorDetails,
        getCartErrorDetails
    } = useCartErrorHandler();

    const {
        isProductInCart,
        getCartItemInfo,
        getProductQuantity,
        getCartItemDisplayInfo,
        checkMultipleProducts,

        cartProductIds,
        cartItemsMap,
        hasCartItems,
        totalItemsCount,

        checkProductInCartSync,
        getCartItemInfoSync,
        getProductQuantitySync
    } = useCartItemChecker();

    const addItemToCart = createAddItemHandler({
        isAddingItem,
        setAddingItem,
        clearAddItemError,
        setAddItemError
    });

    const removeItemFromCart = createRemoveItemHandler({
        isRemovingItem,
        setRemovingItem,
        clearRemoveItemError,
        setRemoveItemError
    });

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

        // Remove item state
        isRemovingItem,
        removeItemError,

        // Actions
        initializeCart,
        addItemToCart: (itemData) => addItemToCart(itemData, showNotifications),
        removeItemFromCart: (itemId) => removeItemFromCart(itemId, showNotifications),
        reloadCart,
        switchToUserCart,
        switchToAnonymousCart,
        clearAddItemError,
        clearRemoveItemError,

        // Error handling
        getAddItemErrorDetails,
        getCartErrorDetails,

        // Cart item checking
        isProductInCart,
        getCartItemInfo,
        getProductQuantity,
        getCartItemDisplayInfo,
        checkMultipleProducts,
        cartProductIds,
        cartItemsMap,
        hasCartItems,
        totalItemsCount,

        // Cart item checking
        checkProductInCartSync,
        getCartItemInfoSync,
        getProductQuantitySync
    };
}