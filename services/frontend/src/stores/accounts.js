import {defineStore} from 'pinia'

import accountService from '@/services/accountService'

export const useAccountStore = defineStore('accounts', {
    state: () => ({
        registrationLoading: false,
        registrationError: null,
        registrationSuccess: false,

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
         * Clear registration state
         */
        clearRegistrationState() {
            this.registrationError = null;
            this.registrationSuccess = false;
            this.registrationLoading = false;
        },

        /**
         * Clear all account state
         */
        resetState() {
            this.registrationLoading = false;
            this.registrationError = null;
            this.registrationSuccess = false;
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
        }
    }
});
