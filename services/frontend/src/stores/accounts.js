import {defineStore} from 'pinia'

import accountService from '@/services/accountService'

export const useAccountStore = defineStore('accounts', {
    state: () => ({
        registrationLoading: false,
        registrationError: null,
        registrationSuccess: false,

        activationLoading: false,
        activationError: null,
        activationSuccess: false,

        currentUser: null,
        isAuthenticated: false,
    }),

    getters: {
        isRegistering() {
            return this.registrationLoading;
        },

        hasRegistrationError() {
            return this.registrationError !== null;
        },

        registrationErrorMessage() {
            if (!this.registrationError) return '';

            switch (this.registrationError.status) {
                case 422:
                    if (this.registrationError.field) {
                        return `${this.registrationError.field}: ${this.registrationError.message}`;
                    }
                    return this.registrationError.message || 'Please check your input data';

                case 409:
                    return this.registrationError.message || 'This email address is already registered. Please use a different email or try signing in.';

                case 400:
                    return this.registrationError.message || 'Invalid registration data. Please check your information and try again.';

                case 500:
                    return 'Server error. Please try again later.';

                default:
                    return this.registrationError.message || 'Registration failed. Please try again.';
            }
        },

        isEmailAlreadyExists() {
            return this.registrationError?.status === 409;
        },

        isActivating() {
            return this.activationLoading;
        },

        hasActivationError() {
            return this.activationError !== null;
        },

        activationErrorMessage() {
            if (!this.activationError) return '';

            switch (this.activationError.status) {
                case 404:
                    return this.activationError.message || 'User not found. Please check your email address.';

                case 400:
                    return this.activationError.message || 'Invalid activation data or account already activated.';

                case 410:
                    return this.activationError.message || 'Activation token has expired. Please request a new activation email.';

                case 422:
                    return this.activationError.message || 'Invalid activation link format.';

                case 500:
                    return 'Server error. Please try again later.';

                default:
                    return this.activationError.message || 'Account activation failed. Please try again.';
            }
        },

        userEmail() {
            return this.currentUser?.email || null;
        }
    },

    actions: {
        /**
         * Register a new user
         * @param {Object} userData - User registration data
         * @param {string} userData.email - User email
         * @param {string} userData.password - User password
         * @returns {Promise<Object>} - Registration result
         */
        async register(userData) {
            this.registrationLoading = true;
            this.registrationError = null;
            this.registrationSuccess = false;

            try {
                const response = await accountService.register({
                    email: userData.email,
                    password: userData.password
                });

                this.registrationSuccess = true;

                if (response.user) {
                    this.currentUser = response.user;
                    this.isAuthenticated = true;
                }

                return {
                    success: true,
                    data: response,
                    message: response.message || 'Registration successful'
                };

            } catch (err) {
                this.registrationError = {
                    status: err.status || 500,
                    message: err.message || 'Registration failed',
                    field: err.field || null
                };

                this.registrationSuccess = false;

                return {
                    success: false,
                    error: this.registrationError,
                    message: this.registrationErrorMessage
                };

            } finally {
                this.registrationLoading = false;
            }
        },

        /**
         * Activate user account
         * @param {Object} activationData - Account activation data
         * @param {string} activationData.email - User email
         * @param {string} activationData.token - Activation token
         * @returns {Promise<Object>} - Activation result
         */
        async activate(activationData) {
            this.activationLoading = true;
            this.activationError = null;
            this.activationSuccess = false;

            try {
                const response = await accountService.activate({
                    email: activationData.email,
                    token: activationData.token
                });

                this.activationSuccess = true;

                if (response.user) {
                    this.currentUser = response.user;
                    this.isAuthenticated = true;
                }

                return {
                    success: true,
                    data: response,
                    message: response.message || 'Account activated successfully'
                };

            } catch (err) {
                this.activationError = {
                    status: err.status || 500,
                    message: err.message || 'Account activation failed',
                    field: err.field || null
                };

                this.activationSuccess = false;

                return {
                    success: false,
                    error: this.activationError,
                    message: this.activationErrorMessage
                };

            } finally {
                this.activationLoading = false;
            }
        },

        /**
         * Clear registration state
         */
        clearRegistrationState() {
            this.registrationError = null;
            this.registrationSuccess = false;
            this.registrationLoading = false;
        },

        /**
         * Clear activation state
         */
        clearActivationState() {
            this.activationError = null;
            this.activationSuccess = false;
            this.activationLoading = false;
        },

        /**
         * Clear all account state
         */
        resetState() {
            this.registrationLoading = false;
            this.registrationError = null;
            this.registrationSuccess = false;
            this.activationLoading = false;
            this.activationError = null;
            this.activationSuccess = false;
            this.currentUser = null;
            this.isAuthenticated = false;
        },

        /**
         * Logout user
         */
        logout() {
            this.currentUser = null;
            this.isAuthenticated = false;
            this.clearRegistrationState();
            this.clearActivationState();
        }
    }
});
