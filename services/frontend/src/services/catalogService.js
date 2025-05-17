import api from '@/services/api.js';

const BASE_URL = '/catalog'

/**
 * Service for working with product catalog
 */
export default {
    /**
     * Get products with pagination and optional filters
     * @param {number} page - Page number (1-based)
     * @param {number} perPage - Number of items per page
     * @param {string} ordering - Ordering string
     * @param {Object} filters - Filter parameters
     * @returns {Promise<Object>} - Product data with pagination info
     */
    async getProducts(page = 1, perPage = 10, ordering = null, filters = {}) {
        const params = {page, per_page: perPage}

        if (ordering) {
            params.ordering = ordering
        }

        if (filters.gender) {
            params.gender = filters.gender
        }
        if (filters.min_year) {
            params.min_year = filters.min_year
        }
        if (filters.max_year) {
            params.max_year = filters.max_year
        }

        const response = await api.get(`${BASE_URL}/products`, {params})
        return response.data
    },

    /**
     * Get available filters for products
     * @returns {Promise<Object>} - Filter options
     */
    async getFilters() {
        const response = await api.get(`${BASE_URL}/products/filters`)
        return response.data
    }
}
