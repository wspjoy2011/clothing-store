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
    /**
     * Get products by category with filtering, pagination and sorting
     *
     * @param {number} masterCategoryId - Master category ID (required)
     * @param {number|null} subCategoryId - Subcategory ID (optional)
     * @param {number|null} articleTypeId - Article type ID (optional)
     * @param {number} page - Page number (default: 1)
     * @param {number} perPage - Items per page (default: 12)
     * @param {string} ordering - Ordering parameter (default: '-id')
     * @param {Object} filters - Additional filters (gender, min_year, max_year)
     * @param {string|null} searchQuery - Search query string
     * @returns {Promise<Object>} - Paginated products for the specified category
     */
    async getProductsByCategory(
        masterCategoryId,
        subCategoryId = null,
        articleTypeId = null,
        page = 1,
        perPage = 12,
        ordering = '-id',
        filters = {},
        searchQuery = null
    ) {
        try {
            let url = `${BASE_URL}/categories/${masterCategoryId}/products`;

            if (subCategoryId !== null) {
                url = `${BASE_URL}/categories/${masterCategoryId}/${subCategoryId}/products`;

                if (articleTypeId !== null) {
                    url = `${BASE_URL}/categories/${masterCategoryId}/${subCategoryId}/${articleTypeId}/products`;
                }
            }

            const params = {
                page,
                per_page: perPage,
                ordering,
                ...filters
            };

            if (searchQuery && searchQuery.trim()) {
                params.q = searchQuery.trim();
            }

            const response = await api.get(url, {params});
            return response.data;
        } catch (error) {
            console.error('Error fetching products by category:', error);
            throw error;
        }
    },
    /**
     * Get available filters for products in specific categories
     * @param {number} masterCategoryId - Master category ID (required)
     * @param {number|null} subCategoryId - Subcategory ID (optional)
     * @param {number|null} articleTypeId - Article type ID (optional)
     * @returns {Promise<Object>} - Filter options for the specified categories
     */
    async getFiltersByCategory(masterCategoryId, subCategoryId = null, articleTypeId = null) {
        try {
            let url = `${BASE_URL}/categories/${masterCategoryId}/filters`;

            if (subCategoryId !== null) {
                url = `${BASE_URL}/categories/${masterCategoryId}/${subCategoryId}/filters`;

                if (articleTypeId !== null) {
                    url = `${BASE_URL}/categories/${masterCategoryId}/${subCategoryId}/${articleTypeId}/filters`;
                }
            }

            const response = await api.get(url);
            return response.data;
        } catch (error) {
            console.error('Error fetching category filters:', error);
            throw error;
        }
    }
};
