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

    const addItemToCart = async (itemData, showNotifications = true) => {
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
        addItemToCart,
        reloadCart,
        switchToUserCart,
        switchToAnonymousCart
    };
}
