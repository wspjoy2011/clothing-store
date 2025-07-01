import {defineStore} from 'pinia'

import accountService from '@/services/accountService'
import socialAuthService from '@/services/socialAuthService'
import {
    parseApiError,
    checkErrorCondition,
    createErrorObject,
    createSuccessResult,
    createErrorResult,
    storage
} from './helpers'

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
        accessToken: storage.get('accessToken') || null,
        refreshToken: storage.get('refreshToken') || null,

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
            return parseApiError(this.registrationError, 'registration');
        },

        isEmailAlreadyExists() {
            return checkErrorCondition(this.registrationError, 'emailAlreadyExists');
        },

        isLoggingIn() {
            return this.loginLoading;
        },

        hasLoginError() {
            return this.loginError !== null;
        },

        loginErrorMessage() {
            return parseApiError(this.loginError, 'login');
        },

        needsActivation() {
            return checkErrorCondition(this.loginError, 'needsActivation');
        },

        needsRegistration() {
            return checkErrorCondition(this.loginError, 'needsRegistration');
        },

        isActivating() {
            return this.activationLoading;
        },

        hasActivationError() {
            return this.activationError !== null;
        },

        activationErrorMessage() {
            return parseApiError(this.activationError, 'activation');
        },

        isTokenExpired() {
            return checkErrorCondition(this.activationError, 'tokenExpired');
        },

        isResending() {
            return this.resendLoading;
        },

        hasResendError() {
            return this.resendError !== null;
        },

        resendErrorMessage() {
            return parseApiError(this.resendError, 'resend');
        },

        isLoggingOut() {
            return this.logoutLoading;
        },

        hasLogoutError() {
            return this.logoutError !== null;
        },

        logoutErrorMessage() {
            return parseApiError(this.logoutError, 'logout');
        },

        isLoadingUser() {
            return this.userLoading;
        },

        hasUserError() {
            return this.userError !== null;
        },

        userErrorMessage() {
            return parseApiError(this.userError, 'user');
        },

        isSocialAuthenticating() {
            return this.socialAuthLoading;
        },

        hasSocialAuthError() {
            return this.socialAuthError !== null;
        },

        socialAuthErrorMessage() {
            return parseApiError(this.socialAuthError, 'social');
        },

        socialAuthWasNewUser() {
            return this.socialAuthResult?.is_new_user || false;
        },

        socialAuthMessage() {
            return this.socialAuthResult?.message || '';
        },

        userEmail() {
            return this.currentUser?.email || storage.get('userEmail') || null;
        },

        userName() {
            return this.currentUser?.email || storage.get('userName') || null;
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
        /**
         * Set authentication tokens
         * @param {Object} tokens - Token object
         * @param {string} tokens.access_token - Access token
         * @param {string} tokens.refresh_token - Refresh token
         */
        setTokens(tokens) {
            if (tokens.access_token) {
                this.accessToken = tokens.access_token;
                storage.set('accessToken', tokens.access_token);
            }
            if (tokens.refresh_token) {
                this.refreshToken = tokens.refresh_token;
                storage.set('refreshToken', tokens.refresh_token);
            }
            this.isAuthenticated = !!this.refreshToken;
        },

        /**
         * Set user data
         * @param {Object} user - User object
         * @param {string} user.email - User email
         * @param {string} user.name - User name
         * @param {number} user.id - User ID
         * @param {string} user.group_name - User group
         */
        setUser(user) {
            this.currentUser = user;

            if (user.email) {
                storage.set('userEmail', user.email);
            }
            if (user.name) {
                storage.set('userName', user.name);
            }
            if (user.id) {
                storage.set('userId', user.id.toString());
            }
            if (user.group_name) {
                storage.set('userGroup', user.group_name);
            }
        },

        /**
         * Clear authentication tokens
         */
        clearTokens() {
            this.accessToken = null;
            this.refreshToken = null;
            this.isAuthenticated = false;
            storage.remove('accessToken', 'refreshToken');
        },

        /**
         * Clear user data
         */
        clearUser() {
            this.currentUser = null;
            storage.remove('userEmail', 'userId', 'userGroup', 'userName');
        },

        async initializeAuth() {
            if (this.isInitialized) {
                return;
            }

            try {
                const refreshToken = storage.get('refreshToken');

                if (refreshToken) {
                    this.refreshToken = refreshToken;
                    this.accessToken = storage.get('accessToken');

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

                    const userEmail = storage.get('userEmail');
                    if (userEmail) {
                        console.warn('Found userEmail in localStorage but no refresh token, clearing...');
                        this.clearUser();
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
                return createErrorResult(
                    createErrorObject(null, 'No refresh token available'),
                    'user'
                );
            }

            this.userLoading = true;
            this.userError = null;

            try {
                const response = await accountService.getCurrentUser(this.refreshToken);

                if (response.user) {
                    this.setUser(response.user);
                }

                return createSuccessResult(response, 'User data loaded successfully');

            } catch (err) {
                this.userError = createErrorObject(err, 'Failed to load user data');

                if (err.status === 401) {
                    console.warn('Refresh token expired or invalid, clearing auth state');
                    this.clearLocalState();
                }

                return createErrorResult(this.userError, 'user');

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
         * Authenticate with Facebook OAuth
         * @param {string} accessToken - Facebook OAuth access token
         * @returns {Promise<Object>} - Social authentication result
         */
        async authenticateWithFacebook(accessToken) {
            return this.socialAuthenticate('facebook', accessToken);
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
                    this.setTokens(response.tokens);
                }

                if (response.user_profile) {
                    this.setUser({
                        email: response.user_profile.email,
                        name: response.user_profile.name
                    });
                }

                return {
                    success: true,
                    data: response,
                    message: response.message || `${provider} authentication successful`,
                    isNewUser: response.is_new_user || false
                };

            } catch (err) {
                this.socialAuthError = createErrorObject(err, 'Social authentication failed');
                this.socialAuthError.provider = provider;
                this.socialAuthSuccess = false;

                return {
                    success: false,
                    error: this.socialAuthError,
                    message: parseApiError(this.socialAuthError, 'social'),
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
                    storage.set('userEmail', response.user.email);
                }

                return createSuccessResult(response, 'Registration successful');

            } catch (err) {
                this.registrationError = createErrorObject(err, 'Registration failed');
                this.registrationSuccess = false;

                return createErrorResult(this.registrationError, 'registration');

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

                this.setTokens({
                    access_token: response.access_token,
                    refresh_token: response.refresh_token
                });

                await this.loadCurrentUser();

                return createSuccessResult(response, 'Login successful');

            } catch (err) {
                this.loginError = createErrorObject(err, 'Login failed');
                this.loginSuccess = false;

                return createErrorResult(this.loginError, 'login');

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
                const refreshToken = this.refreshToken || storage.get('refreshToken');

                if (refreshToken) {
                    await accountService.logout({
                        refresh_token: refreshToken
                    });
                }

                this.clearLocalState();

                return createSuccessResult(null, 'Logout successful');

            } catch (err) {
                this.logoutError = createErrorObject(err, 'Logout failed on server');
                this.clearLocalState();

                return {
                    success: true,
                    message: 'Logout completed (with server warning)',
                    warning: parseApiError(this.logoutError, 'logout')
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
                    this.setUser(response.user);
                }

                return createSuccessResult(response, 'Account activated successfully');

            } catch (err) {
                this.activationError = createErrorObject(err, 'Account activation failed');
                this.activationSuccess = false;

                return createErrorResult(this.activationError, 'activation');

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

                return createSuccessResult(response, 'Activation email sent successfully');

            } catch (err) {
                this.resendError = createErrorObject(err, 'Failed to send activation email');
                this.resendSuccess = false;

                return createErrorResult(this.resendError, 'resend');

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
            this.clearTokens();
            this.clearUser();
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
