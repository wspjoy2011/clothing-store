import {useCartStore} from '@/stores/cart.js';
import {useNotifications} from '@/composables/accounts/useNotifications.js';

export function useCartActions() {
    const cartStore = useCartStore();
    const {showSuccess, showError} = useNotifications();

    const initializeCart = async () => {
        try {
            await cartStore.initializeCart();
        } catch (error) {
            throw error;
        }
    };

    const baseAddItemToCart = async (itemData, showNotify = true) => {
        try {
            const result = await cartStore.addItemToCart(itemData);

            if (showNotify) {
                showSuccess('Item added to cart successfully!');
            }

            return result;
        } catch (error) {
            if (showNotify) {
                showError(error.message || 'Failed to add item to cart');
            }
            throw error;
        }
    };

    const baseRemoveItemFromCart = async (itemId, showNotify = true) => {
        try {
            await cartStore.removeItemFromCart(itemId);

            if (showNotify) {
                showSuccess('Item removed from cart successfully!');
            }
        } catch (error) {
            if (showNotify) {
                showError(error.message || 'Failed to remove item from cart');
            }
            throw error;
        }
    };

    const baseUpdateItemInCart = async (itemId, itemData, showNotify = true) => {
        try {
            const result = await cartStore.updateItemInCart(itemId, itemData);

            if (showNotify) {
                showSuccess('Item quantity updated');
            }

            return result;
        } catch (error) {
            if (showNotify) {
                showError(error.message || 'Failed to update item quantity');
            }
            throw error;
        }
    };

    const createAddItemHandler = (stateHandlers) => {
        const { isAddingItem, setAddingItem, clearAddItemError, setAddItemError } = stateHandlers;

        return async (itemData, showNotify = true) => {
            if (isAddingItem.value) return;

            setAddingItem(true);
            clearAddItemError();

            try {
                return await baseAddItemToCart(itemData, showNotify);
            } catch (error) {
                setAddItemError(error.message);
                throw error;
            } finally {
                setAddingItem(false);
            }
        };
    };

    const createRemoveItemHandler = (stateHandlers) => {
        const { isRemovingItem, setRemovingItem, clearRemoveItemError, setRemoveItemError } = stateHandlers;

        return async (itemId, showNotify = true) => {
            if (isRemovingItem.value) return;

            setRemovingItem(true);
            clearRemoveItemError();

            try {
                return await baseRemoveItemFromCart(itemId, showNotify);
            } catch (error) {
                setRemoveItemError(error.message);
                throw error;
            } finally {
                setRemovingItem(false);
            }
        };
    };

    const reloadCart = async () => {
        try {
            await cartStore.reloadCart();
        } catch (error) {
            throw error;
        }
    };

    const switchToUserCart = async () => {
        try {
            await cartStore.switchToUserCart();
        } catch (error) {
            throw error;
        }
    };

    const switchToAnonymousCart = async () => {
        try {
            await cartStore.switchToAnonymousCart();
        } catch (error) {
            throw error;
        }
    };

    return {
        initializeCart,

        addItemToCart: baseAddItemToCart,
        removeItemFromCart: baseRemoveItemFromCart,
        updateItemInCart: baseUpdateItemInCart,

        baseAddItemToCart,
        baseRemoveItemFromCart,
        baseUpdateItemInCart,

        createAddItemHandler,
        createRemoveItemHandler,

        reloadCart,
        switchToUserCart,
        switchToAnonymousCart
    };
}
