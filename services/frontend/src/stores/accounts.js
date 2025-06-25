import {defineStore} from 'pinia'

import accountService from '@/services/accountService'
import socialAuthService from '@/services/socialAuthService'

export const useAccountStore = defineStore('accounts', {
    state: () => ({
        registrationLoading: false,
        registrationError: null,
        registrationSuccess: false,

        loginLoading: false,
        loginError: null,
        loginSuccess: false,

        activationLoading: false,
        activationError: null,
        activationSuccess: false,

        resendLoading: false,
        resendError: null,
        resendSuccess: false,

        logoutLoading: false,
        logoutError: null,

        userLoading: false,
        userError: null,

        socialAuthLoading: false,
        socialAuthError: null,
        socialAuthSuccess: false,
        socialAuthResult: null,

        currentUser: null,
        isAuthenticated: false,
        accessToken: localStorage.getItem('accessToken') || null,
        refreshToken: localStorage.getItem('refreshToken') || null,

        isInitialized: false,
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

        isLoggingIn() {
            return this.loginLoading;
        },

        hasLoginError() {
            return this.loginError !== null;
        },

        loginErrorMessage() {
            if (!this.loginError) return '';

            switch (this.loginError.status) {
                case 403:
                    return this.loginError.message || 'Account not activated. Please check your email for activation instructions.';

                case 404:
                    return this.loginError.message || 'User not found. Please check your credentials or register a new account.';

                case 400:
                    return this.loginError.message || 'Invalid login credentials. Please check your email and password.';

                case 422:
                    if (this.loginError.field) {
                        return `${this.loginError.field}: ${this.loginError.message}`;
                    }
                    return this.loginError.message || 'Please check your input data';

                case 500:
                    return 'Server error. Please try again later.';

                default:
                    return this.loginError.message || 'Login failed. Please try again.';
            }
        },

        needsActivation() {
            return this.loginError?.status === 403;
        },

        needsRegistration() {
            return this.loginError?.status === 404;
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

        isTokenExpired() {
            return this.activationError?.status === 410;
        },

        isResending() {
            return this.resendLoading;
        },

        hasResendError() {
            return this.resendError !== null;
        },

        resendErrorMessage() {
            if (!this.resendError) return '';

            switch (this.resendError.status) {
                case 404:
                    return this.resendError.message || 'User not found. Please check your email address.';

                case 400:
                    return this.resendError.message || 'This account is already activated or invalid request.';

                case 422:
                    return this.resendError.message || 'Please enter a valid email address.';

                case 500:
                    return 'Server error. Please try again later.';

                default:
                    return this.resendError.message || 'Failed to send activation email. Please try again.';
            }
        },

        isLoggingOut() {
            return this.logoutLoading;
        },

        hasLogoutError() {
            return this.logoutError !== null;
        },

        logoutErrorMessage() {
            if (!this.logoutError) return '';

            switch (this.logoutError.status) {
                case 400:
                    return this.logoutError.message || 'Invalid logout request.';

                case 401:
                    return this.logoutError.message || 'Unauthorized logout attempt.';

                case 500:
                    return 'Server error during logout. Please try again later.';

                default:
                    return this.logoutError.message || 'Logout failed. Please try again.';
            }
        },

        isLoadingUser() {
            return this.userLoading;
        },

        hasUserError() {
            return this.userError !== null;
        },

        userErrorMessage() {
            if (!this.userError) return '';

            switch (this.userError.status) {
                case 401:
                    return this.userError.message || 'Session expired. Please login again.';

                case 404:
                    return this.userError.message || 'User not found.';

                case 500:
                    return 'Server error. Please try again later.';

                default:
                    return this.userError.message || 'Failed to load user data.';
            }
        },

        // Social auth getters
        isSocialAuthenticating() {
            return this.socialAuthLoading;
        },

        hasSocialAuthError() {
            return this.socialAuthError !== null;
        },

        socialAuthErrorMessage() {
            if (!this.socialAuthError) return '';

            switch (this.socialAuthError.status) {
                case 400:
                    return this.socialAuthError.message || 'Invalid social authentication request';

                case 401:
                    return this.socialAuthError.message || 'Invalid access token from social provider';

                case 422:
                    return this.socialAuthError.message || 'Validation error during social authentication';

                case 503:
                    return this.socialAuthError.message || 'Social authentication service temporarily unavailable';

                case 500:
                    return 'Server error during social authentication. Please try again later.';

                default:
                    return this.socialAuthError.message || 'Social authentication failed. Please try again.';
            }
        },

        socialAuthWasNewUser() {
            return this.socialAuthResult?.is_new_user || false;
        },

        socialAuthMessage() {
            return this.socialAuthResult?.message || '';
        },

        userEmail() {
            return this.currentUser?.email || localStorage.getItem('userEmail') || null;
        },

        userName() {
            return this.currentUser?.email || localStorage.getItem('userName') || null;
        },

        hasTokens() {
            return !!this.refreshToken;
        },

        hasUserData() {
            return !!this.currentUser;
        },

        authStatus() {
            if (!this.isInitialized) {
                return 'initializing';
            }
            return this.refreshToken ? 'authenticated' : 'unauthenticated';
        }
    },

    actions: {
        async initializeAuth() {
            if (this.isInitialized) {
                return;
            }

            try {
                const refreshToken = localStorage.getItem('refreshToken');

                if (refreshToken) {
                    this.refreshToken = refreshToken;
                    this.accessToken = localStorage.getItem('accessToken');

                    const userResult = await this.loadCurrentUser();

                    if (userResult.success) {
                        this.isAuthenticated = true;
                    } else {
                        console.warn('Failed to load user with refresh token, clearing auth state');
                        this.clearLocalState();
                    }
                } else {
                    this.isAuthenticated = false;
                    this.currentUser = null;
                    this.accessToken = null;

                    const userEmail = localStorage.getItem('userEmail');
                    if (userEmail) {
                        console.warn('Found userEmail in localStorage but no refresh token, clearing...');
                        localStorage.removeItem('userEmail');
                        localStorage.removeItem('userId');
                        localStorage.removeItem('userGroup');
                        localStorage.removeItem('userName');
                    }
                }

            } catch (error) {
                console.error('Error during auth initialization:', error);
                this.clearLocalState();
            } finally {
                this.isInitialized = true;
            }
        },

        /**
         * Load current user data by refresh token
         * @returns {Promise<Object>} - Load user result
         */
        async loadCurrentUser() {
            if (!this.refreshToken) {
                return {
                    success: false,
                    message: 'No refresh token available'
                };
            }

            this.userLoading = true;
            this.userError = null;

            try {
                const response = await accountService.getCurrentUser(this.refreshToken);

                if (response.user) {
                    this.currentUser = response.user;

                    localStorage.setItem('userEmail', response.user.email);
                    if (response.user.id) {
                        localStorage.setItem('userId', response.user.id.toString());
                    }
                    if (response.user.group_name) {
                        localStorage.setItem('userGroup', response.user.group_name);
                    }
                }

                return {
                    success: true,
                    data: response,
                    message: response.message || 'User data loaded successfully'
                };

            } catch (err) {
                this.userError = {
                    status: err.status || 500,
                    message: err.message || 'Failed to load user data',
                };

                if (err.status === 401) {
                    console.warn('Refresh token expired or invalid, clearing auth state');
                    this.clearLocalState();
                }

                return {
                    success: false,
                    error: this.userError,
                    message: this.userErrorMessage
                };

            } finally {
                this.userLoading = false;
            }
        },

        /**
         * Authenticate with Google OAuth
         * @param {string} accessToken - Google OAuth access token
         * @returns {Promise<Object>} - Social authentication result
         */
        async authenticateWithGoogle(accessToken) {
            return this.socialAuthenticate('google', accessToken);
        },

        /**
         * Authenticate with social OAuth provider
         * @param {string} provider - OAuth provider name
         * @param {string} accessToken - OAuth access token
         * @returns {Promise<Object>} - Social authentication result
         */
        async socialAuthenticate(provider, accessToken) {
            this.socialAuthLoading = true;
            this.socialAuthError = null;
            this.socialAuthSuccess = false;
            this.socialAuthResult = null;

            try {
                const response = await socialAuthService.authenticate({
                    provider,
                    access_token: accessToken
                });

                this.socialAuthSuccess = true;
                this.socialAuthResult = response;

                if (response.tokens) {
                    if (response.tokens.access_token) {
                        this.accessToken = response.tokens.access_token;
                        localStorage.setItem('accessToken', response.tokens.access_token);
                    }

                    if (response.tokens.refresh_token) {
                        this.refreshToken = response.tokens.refresh_token;
                        localStorage.setItem('refreshToken', response.tokens.refresh_token);
                    }
                }

                if (response.user_profile) {
                    this.currentUser = {
                        email: response.user_profile.email,
                        name: response.user_profile.name
                    };
                    localStorage.setItem('userEmail', response.user_profile.email);
                    if (response.user_profile.name) {
                        localStorage.setItem('userName', response.user_profile.name);
                    }
                }

                this.isAuthenticated = !!this.refreshToken;

                return {
                    success: true,
                    data: response,
                    message: response.message || `${provider} authentication successful`,
                    isNewUser: response.is_new_user || false
                };

            } catch (err) {
                this.socialAuthError = {
                    status: err.status || 500,
                    message: err.message || 'Social authentication failed',
                    provider: provider
                };

                this.socialAuthSuccess = false;

                return {
                    success: false,
                    error: this.socialAuthError,
                    message: this.socialAuthErrorMessage,
                    provider: provider
                };

            } finally {
                this.socialAuthLoading = false;
            }
        },

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
                    localStorage.setItem('userEmail', response.user.email);
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
         * Login user
         * @param {Object} loginData - User login data
         * @param {string} loginData.email - User email
         * @param {string} loginData.password - User password
         * @returns {Promise<Object>} - Login result
         */
        async login(loginData) {
            this.loginLoading = true;
            this.loginError = null;
            this.loginSuccess = false;

            try {
                const response = await accountService.login({
                    email: loginData.email,
                    password: loginData.password
                });

                this.loginSuccess = true;

                if (response.access_token) {
                    this.accessToken = response.access_token;
                    localStorage.setItem('accessToken', response.access_token);
                }

                if (response.refresh_token) {
                    this.refreshToken = response.refresh_token;
                    localStorage.setItem('refreshToken', response.refresh_token);
                }

                this.isAuthenticated = !!this.refreshToken;

                await this.loadCurrentUser();

                return {
                    success: true,
                    data: response,
                    message: response.message || 'Login successful'
                };

            } catch (err) {
                this.loginError = {
                    status: err.status || 500,
                    message: err.message || 'Login failed',
                    field: err.field || null
                };

                this.loginSuccess = false;

                return {
                    success: false,
                    error: this.loginError,
                    message: this.loginErrorMessage
                };

            } finally {
                this.loginLoading = false;
            }
        },

        /**
         * Logout user
         * @returns {Promise<Object>} - Logout result
         */
        async logout() {
            this.logoutLoading = true;
            this.logoutError = null;

            try {
                const refreshToken = this.refreshToken || localStorage.getItem('refreshToken');

                if (refreshToken) {
                    await accountService.logout({
                        refresh_token: refreshToken
                    });
                }

                this.clearLocalState();

                return {
                    success: true,
                    message: 'Logout successful'
                };

            } catch (err) {
                this.logoutError = {
                    status: err.status || 500,
                    message: err.message || 'Logout failed on server',
                    field: err.field || null
                };

                this.clearLocalState();

                return {
                    success: true,
                    message: 'Logout completed (with server warning)',
                    warning: this.logoutErrorMessage
                };

            } finally {
                this.logoutLoading = false;
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
                    localStorage.setItem('userEmail', response.user.email);
                    if (response.user.id) {
                        localStorage.setItem('userId', response.user.id.toString());
                    }
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
         * Resend activation email
         * @param {Object} resendData - Resend activation data
         * @param {string} resendData.email - User email
         * @returns {Promise<Object>} - Resend result
         */
        async resendActivation(resendData) {
            this.resendLoading = true;
            this.resendError = null;
            this.resendSuccess = false;

            try {
                const response = await accountService.resendActivation({
                    email: resendData.email
                });

                this.resendSuccess = true;

                return {
                    success: true,
                    data: response,
                    message: response.message || 'Activation email sent successfully'
                };

            } catch (err) {
                this.resendError = {
                    status: err.status || 500,
                    message: err.message || 'Failed to send activation email',
                    field: err.field || null
                };

                this.resendSuccess = false;

                return {
                    success: false,
                    error: this.resendError,
                    message: this.resendErrorMessage
                };

            } finally {
                this.resendLoading = false;
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
         * Clear login state
         */
        clearLoginState() {
            this.loginError = null;
            this.loginSuccess = false;
            this.loginLoading = false;
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
         * Clear resend state
         */
        clearResendState() {
            this.resendError = null;
            this.resendSuccess = false;
            this.resendLoading = false;
        },

        /**
         * Clear logout state
         */
        clearLogoutState() {
            this.logoutError = null;
            this.logoutLoading = false;
        },

        /**
         * Clear user data state
         */
        clearUserState() {
            this.userError = null;
            this.userLoading = false;
        },

        /**
         * Clear social auth state
         */
        clearSocialAuthState() {
            this.socialAuthError = null;
            this.socialAuthSuccess = false;
            this.socialAuthLoading = false;
            this.socialAuthResult = null;
        },

        /**
         * Clear all account state
         */
        resetState() {
            this.registrationLoading = false;
            this.registrationError = null;
            this.registrationSuccess = false;
            this.loginLoading = false;
            this.loginError = null;
            this.loginSuccess = false;
            this.activationLoading = false;
            this.activationError = null;
            this.activationSuccess = false;
            this.resendLoading = false;
            this.resendError = null;
            this.resendSuccess = false;
            this.logoutLoading = false;
            this.logoutError = null;
            this.userLoading = false;
            this.userError = null;
            this.socialAuthLoading = false;
            this.socialAuthError = null;
            this.socialAuthSuccess = false;
            this.socialAuthResult = null;
            this.currentUser = null;
            this.isAuthenticated = false;
        },

        /**
         * Clear local authentication state
         * (used internally by logout and initializeAuth)
         */
        clearLocalState() {
            this.currentUser = null;
            this.isAuthenticated = false;
            this.accessToken = null;
            this.refreshToken = null;

            localStorage.removeItem('accessToken');
            localStorage.removeItem('refreshToken');
            localStorage.removeItem('userEmail');
            localStorage.removeItem('userId');
            localStorage.removeItem('userGroup');
            localStorage.removeItem('userName');

            this.clearRegistrationState();
            this.clearLoginState();
            this.clearActivationState();
            this.clearResendState();
            this.clearLogoutState();
            this.clearUserState();
            this.clearSocialAuthState();
        }
    }
});
