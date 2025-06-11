import api from '@/services/api.js';

const BASE_URL = '/accounts'

/**
 * Service for working with user accounts
 */
export default {
    /**
     * Register a new user account
     * @param {Object} userData - User registration data
     * @param {string} userData.email - User email address
     * @param {string} userData.password - User password
     * @returns {Promise<Object>} - Registration response data
     */
    async register(userData) {
        const response = await api.post(`${BASE_URL}/register`, userData);
        return response.data;
    }
}
