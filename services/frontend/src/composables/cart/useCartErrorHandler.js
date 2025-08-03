import {computed} from 'vue';
import {useCartStore} from '@/stores/cart.js';

export function useCartErrorHandler() {
    const cartStore = useCartStore();

    const getAddItemErrorDetails = computed(() => {
        const error = cartStore.error;

        if (!error) return null;

        if (error.includes('Insufficient stock') || error.includes('stock')) {
            return {
                icon: 'mdi-package-variant-closed',
                title: 'Out of Stock',
                message: 'This item is currently out of stock',
                canRetry: false,
                actionText: 'View Similar Items'
            };
        }

        if (error.includes('Product') && error.includes('not found')) {
            return {
                icon: 'mdi-package-variant-remove',
                title: 'Product Not Found',
                message: 'This product is no longer available',
                canRetry: false,
                actionText: 'Continue Shopping'
            };
        }

        if (error.includes('Quantity') || error.includes('validation')) {
            return {
                icon: 'mdi-alert-circle',
                title: 'Invalid Quantity',
                message: 'Please select a valid quantity (1-999)',
                canRetry: true,
                actionText: 'Try Again'
            };
        }

        if (error.includes('Authorization') || error.includes('401')) {
            return {
                icon: 'mdi-account-alert',
                title: 'Authentication Required',
                message: 'Please log in to add items to cart',
                canRetry: false,
                actionText: 'Log In'
            };
        }

        return {
            icon: 'mdi-cart-remove',
            title: 'Add to Cart Failed',
            message: 'Unable to add item to cart. Please try again.',
            canRetry: true,
            actionText: 'Retry'
        };
    });

    const getCartErrorDetails = computed(() => {
        const error = cartStore.error;

        if (!error) return null;

        if (error.includes('token') && error.includes('expired')) {
            return {
                icon: 'mdi-clock-alert',
                title: 'Cart Session Expired',
                message: 'Your cart session has expired. Starting fresh.',
                canRetry: true,
                actionText: 'Refresh Cart'
            };
        }

        if (error.includes('Network') || error.includes('connection')) {
            return {
                icon: 'mdi-wifi-off',
                title: 'Connection Error',
                message: 'Unable to connect to server. Check your internet connection.',
                canRetry: true,
                actionText: 'Retry'
            };
        }

        return {
            icon: 'mdi-cart-off',
            title: 'Cart Error',
            message: 'Unable to load cart data. Please try again.',
            canRetry: true,
            actionText: 'Retry'
        };
    });

    return {
        getAddItemErrorDetails,
        getCartErrorDetails
    };
}
