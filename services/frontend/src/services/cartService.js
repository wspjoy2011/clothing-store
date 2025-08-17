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
    },

    /**
     * Remove item from cart for anonymous user by token
     * @param {string} token - Cart token
     * @param {number} itemId - Cart item ID to remove
     * @returns {Promise<void>} - Empty response (HTTP 204)
     */
    async removeItemFromCartByToken(token, itemId) {
        await api.delete(`${BASE_URL}/cart/token/${token}/items/${itemId}`);
    },

    /**
     * Remove item from cart for authenticated user
     * @param {number} itemId - Cart item ID to remove
     * @returns {Promise<void>} - Empty response (HTTP 204)
     */
    async removeItemFromCart(itemId) {
        await api.delete(`${BASE_URL}/cart/items/${itemId}`);
    },

    /**
     * Update item quantity for anonymous user by token
     * @param {string} token - Cart token
     * @param {number} itemId - Cart item ID to update
     * @param {Object} itemData - Update payload { quantity }
     * @returns {Promise<Object>} - Updated cart item data
     */
    async updateItemInCartByToken(token, itemId, itemData) {
        const payload = {
            cart_item_id: itemId,
            quantity: itemData.quantity
        };
        const response = await api.put(`${BASE_URL}/cart/token/${token}/items/${itemId}`, payload);
        return response.data;
    },

    /**
     * Update item quantity for authenticated user
     * @param {number} itemId - Cart item ID to update
     * @param {Object} itemData - Update payload { quantity }
     * @returns {Promise<Object>} - Updated cart item data
     */
    async updateItemInCart(itemId, itemData) {
        const payload = {
            cart_item_id: itemId,
            quantity: itemData.quantity
        };
        const response = await api.put(`${BASE_URL}/cart/items/${itemId}`, payload);
        return response.data;
    }
}
