import {useCartStore} from '@/stores/cart.js';
import {useNotifications} from '@/composables/accounts/useNotifications.js';

export function useCartActions() {
    const cartStore = useCartStore();
    const {showSuccess, showError} = useNotifications();

    const initializeCart = async () => {
        try {
            await cartStore.initializeCart();
        } catch (error) {
            console.error('Failed to initialize cart:', error);
            throw error;
        }
    };

    const baseAddItemToCart = async (itemData, showNotifications = true) => {
        try {
            const result = await cartStore.addItemToCart(itemData);

            if (showNotifications) {
                showSuccess(`Item added to cart successfully!`);
            }

            return result;
        } catch (error) {
            if (showNotifications) {
                showError(error.message || 'Failed to add item to cart');
            }
            throw error;
        }
    };

    const baseRemoveItemFromCart = async (itemId, showNotifications = true) => {
        try {
            await cartStore.removeItemFromCart(itemId);

            if (showNotifications) {
                showSuccess(`Item removed from cart successfully!`);
            }
        } catch (error) {
            if (showNotifications) {
                showError(error.message || 'Failed to remove item from cart');
            }
            throw error;
        }
    };

    const createAddItemHandler = (stateHandlers) => {
        const { isAddingItem, setAddingItem, clearAddItemError, setAddItemError } = stateHandlers;

        return async (itemData, showNotifications = true) => {
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
    };

    const createRemoveItemHandler = (stateHandlers) => {
        const { isRemovingItem, setRemovingItem, clearRemoveItemError, setRemoveItemError } = stateHandlers;

        return async (itemId, showNotifications = true) => {
            if (isRemovingItem.value) return;

            setRemovingItem(true);
            clearRemoveItemError();

            try {
                return await baseRemoveItemFromCart(itemId, showNotifications);
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
            console.error('Failed to reload cart:', error);
            throw error;
        }
    };

    const switchToUserCart = async () => {
        try {
            await cartStore.switchToUserCart();
        } catch (error) {
            console.error('Failed to switch to user cart:', error);
            throw error;
        }
    };

    const switchToAnonymousCart = async () => {
        try {
            await cartStore.switchToAnonymousCart();
        } catch (error) {
            console.error('Failed to switch to anonymous cart:', error);
            throw error;
        }
    };

    return {
        initializeCart,

        addItemToCart: baseAddItemToCart,
        removeItemFromCart: baseRemoveItemFromCart,

        baseAddItemToCart,
        baseRemoveItemFromCart,

        createAddItemHandler,
        createRemoveItemHandler,

        reloadCart,
        switchToUserCart,
        switchToAnonymousCart
    };
}
