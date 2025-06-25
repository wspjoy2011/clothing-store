import api from '@/services/api.js';

const BASE_URL = '/auth'

/**
 * Service for working with social authentication (OAuth providers)
 */
export default {
    /**
     * Authenticate user via social OAuth provider
     * @param {Object} authData - Social authentication data
     * @param {string} authData.provider - OAuth provider name (e.g., 'google', 'facebook')
     * @param {string} authData.access_token - OAuth access token from the provider
     * @returns {Promise<Object>} - Social authentication response data
     */
    async authenticate(authData) {
        const response = await api.post(`${BASE_URL}/social-auth`, authData);
        return response.data;
    },

    /**
     * Get list of supported OAuth providers
     * @returns {Promise<Object>} - List of supported providers and total count
     */
    async getSupportedProviders() {
        const response = await api.get(`${BASE_URL}/social-auth/providers`);
        return response.data;
    },

    /**
     * Authenticate with Google OAuth
     * @param {string} accessToken - Google OAuth access token
     * @returns {Promise<Object>} - Authentication response data
     */
    async authenticateWithGoogle(accessToken) {
        return this.authenticate({
            provider: 'google',
            access_token: accessToken
        });
    },

    /**
     * Authenticate with Facebook OAuth
     * @param {string} accessToken - Facebook OAuth access token
     * @returns {Promise<Object>} - Authentication response data
     */
    async authenticateWithFacebook(accessToken) {
        return this.authenticate({
            provider: 'facebook',
            access_token: accessToken
        });
    },

    /**
     * Test connection to social auth endpoints
     * @returns {Promise<Object>} - Test result with provider information
     */
    async testConnection() {
        try {
            const providersResult = await this.getSupportedProviders();
            return {
                success: true,
                message: 'Social auth service is available',
                providers: providersResult.providers,
                total_providers: providersResult.total_count
            };
        } catch (error) {
            return {
                success: false,
                message: 'Social auth service is unavailable',
                error: error.message || 'Unknown error'
            };
        }
    }
}
