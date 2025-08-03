import api from '@/services/api.js';

const BASE_URL = '/checkout'

/**
 * Service for working with shopping cart
 */
export default {
    /**
     * Create cart token for anonymous users
     * @returns {Promise<Object>} - Cart token data with expiration
     */
    async createCartToken() {
        const response = await api.post(`${BASE_URL}/cart/token`);
        return response.data;
    },

    /**
     * Get cart by token (for anonymous users)
     * @param {string} token - Cart token
     * @returns {Promise<Object>} - Cart data with items and totals
     */
    async getCartByToken(token) {
        const response = await api.post(`${BASE_URL}/cart/token/get`, {
            token: token
        });
        return response.data;
    },

    /**
     * Get cart for authenticated user
     * @returns {Promise<Object>} - Cart data with items and totals
     */
    async getCart() {
        const response = await api.get(`${BASE_URL}/cart`);
        return response.data;
    },

    /**
     * Add item to cart for anonymous user by token
     * @param {string} token - Cart token
     * @param {Object} itemData - Item data {product_id, quantity}
     * @returns {Promise<Object>} - Added cart item data
     */
    async addItemToCartByToken(token, itemData) {
        const response = await api.post(`${BASE_URL}/cart/token/${token}/items`, itemData);
        return response.data;
    },

    /**
     * Add item to cart for authenticated user
     * @param {Object} itemData - Item data {product_id, quantity}
     * @returns {Promise<Object>} - Added cart item data
     */
    async addItemToCart(itemData) {
        const response = await api.post(`${BASE_URL}/cart/items`, itemData);
        return response.data;
    }
}
