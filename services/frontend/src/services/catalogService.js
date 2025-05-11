import api from '@/services/api.js';

/**
 * Service for working with product catalog
 */
export default {
  /**
   * Get list of products with pagination
   * @param {number} page - page number (starting from 1)
   * @param {number} perPage - number of items per page
   * @returns {Promise<Object>} - product data and pagination info
   */
  getProducts(page = 1, perPage = 10) {

    return api.get('/catalog/products', {
      params: {
        page,
        per_page: perPage
      }
    })
    .then(response => response.data)
    .catch(error => {
      console.error('Error fetching products:', error);
      throw error;
    });
  }
};
