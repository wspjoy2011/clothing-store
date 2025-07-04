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
    },

    /**
     * Login user
     * @param {Object} loginData - User login data
     * @param {string} loginData.email - User email address
     * @param {string} loginData.password - User password
     * @returns {Promise<Object>} - Login response data
     */
    async login(loginData) {
        const response = await api.post(`${BASE_URL}/login`, loginData);
        return response.data;
    },

    /**
     * Logout user
     * @param {Object} logoutData - User logout data
     * @param {string} logoutData.refresh_token - User refresh token
     * @returns {Promise<Object>} - Logout response data
     */
    async logout(logoutData) {
        const response = await api.post(`${BASE_URL}/logout`, logoutData);
        return response.data;
    },

    /**
     * Get current user by refresh token
     * @param {string} refreshToken - User refresh token
     * @returns {Promise<Object>} - User data response
     */
    async getCurrentUser(refreshToken) {
        const response = await api.get(`${BASE_URL}/me`, {
            headers: {
                'Authorization': `Bearer ${refreshToken}`
            }
        });
        return response.data;
    },

    /**
     * Activate user account
     * @param {Object} activationData - Account activation data
     * @param {string} activationData.email - User email address
     * @param {string} activationData.token - Activation token
     * @returns {Promise<Object>} - Activation response data
     */
    async activate(activationData) {
        const response = await api.post(`${BASE_URL}/activate`, activationData);
        return response.data;
    },

    /**
     * Resend activation email
     * @param {Object} resendData - Resend activation data
     * @param {string} resendData.email - User email address
     * @returns {Promise<Object>} - Resend response data
     */
    async resendActivation(resendData) {
        const response = await api.post(`${BASE_URL}/resend-activation`, resendData);
        return response.data;
    }
}
