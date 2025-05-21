import api from '@/services/api.js';

const BASE_URL = '/catalog';

/**
 * Service for working with product categories
 */
export default {
    /**
     * Get the complete category menu hierarchy
     *
     * This method retrieves a three-level hierarchy:
     * - Master categories at the top level
     * - Subcategories as children of master categories
     * - Article types as children of subcategories
     *
     * @returns {Promise<Object>} - Complete category hierarchy data
     */
    async getCategoryMenu() {
        try {
            const response = await api.get(`${BASE_URL}/categories`);
            return response.data;
        } catch (error) {
            console.error('Error fetching category menu:', error);
            throw error;
        }
    },
};