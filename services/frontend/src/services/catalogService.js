import api from '@/services/api.js';

/**
 * Service for working with product catalog
 */
export default {
  /**
   * Get list of products with pagination
   * @param {number} page - page number (starting from 1)
   * @param {number} perPage - number of items per page
   * @param {string} ordering - ordering parameter (e.g. 'year', '-year', 'id', '-id')
   * @returns {Promise<Object>} - product data and pagination info
   */
  getProducts(page = 1, perPage = 10, ordering = null) {
    const params = {
      page,
      per_page: perPage
    };

    if (ordering) {
      params.ordering = ordering;
    }

    return api.get('/catalog/products', { params })
      .then(response => response.data)
      .catch(error => {
        console.error('Error fetching products:', error);
        throw error;
      });
  }
};
