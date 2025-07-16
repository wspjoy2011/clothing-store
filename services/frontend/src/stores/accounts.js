import {defineStore} from 'pinia'

import accountService from '@/services/accountService'
import socialAuthService from '@/services/socialAuthService'
import {
    parseApiError,
    checkErrorCondition,
    createErrorObject,
    createSuccessResult,
    createErrorResult,
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
        accessToken: null,
        refreshToken: null,

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
            return this.currentUser?.email || null;
        },

        userName() {
            return this.currentUser?.name || this.currentUser?.email || null;
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
        setTokens(tokens) {
            if (tokens.access_token) {
                this.accessToken = tokens.access_token;
            }
            if (tokens.refresh_token) {
                this.refreshToken = tokens.refresh_token;
            }
            this.isAuthenticated = !!this.refreshToken;
        },

        setUser(user) {
            this.currentUser = user;
        },

        clearTokens() {
            this.accessToken = null;
            this.refreshToken = null;
            this.isAuthenticated = false;
        },

        clearUser() {
            this.currentUser = null;
        },

        async initializeAuth() {
            if (this.isInitialized) {
                return;
            }

            try {
                if (this.refreshToken) {
                    const userResult = await this.loadCurrentUser();

                    if (userResult.success) {
                        this.isAuthenticated = true;
                    } else {
                        this.clearLocalState();
                    }
                } else {
                    this.isAuthenticated = false;
                    this.currentUser = null;
                    this.accessToken = null;
                }

            } catch (error) {
                this.clearLocalState();
            } finally {
                this.isInitialized = true;
            }
        },

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
                    this.clearLocalState();
                }

                return createErrorResult(this.userError, 'user');

            } finally {
                this.userLoading = false;
            }
        },

        async authenticateWithGoogle(accessToken) {
            return this.socialAuthenticate('google', accessToken);
        },

        async authenticateWithFacebook(accessToken) {
            return this.socialAuthenticate('facebook', accessToken);
        },

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

                return createSuccessResult(response, 'Registration successful');

            } catch (err) {
                this.registrationError = createErrorObject(err, 'Registration failed');
                this.registrationSuccess = false;

                return createErrorResult(this.registrationError, 'registration');

            } finally {
                this.registrationLoading = false;
            }
        },

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

        async logout() {
            this.logoutLoading = true;
            this.logoutError = null;

            try {
                const refreshToken = this.refreshToken;

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

        async requestPasswordReset(resetData) {
            try {
                const response = await accountService.requestPasswordReset(resetData);
                return {
                    success: true,
                    message: response.message || 'Password reset request sent successfully',
                    data: response
                };
            } catch (error) {
                return {
                    success: false,
                    message: error.response?.data?.detail || 'Failed to send password reset email',
                    error: error.response?.data
                };
            }
        },

        async confirmPasswordReset(confirmData) {
            try {
                const response = await accountService.confirmPasswordReset(confirmData);
                return {
                    success: true,
                    message: response.message || 'Password reset successful',
                    data: response
                };
            } catch (error) {
                return {
                    success: false,
                    message: error.response?.data?.detail || 'Failed to reset password',
                    error: error.response?.data
                };
            }
        },

        async refreshTokens() {
            if (!this.refreshToken) {
                return createErrorResult(
                    createErrorObject(null, 'No refresh token available'),
                    'refresh'
                );
            }

            try {
                const response = await accountService.refreshTokens(this.refreshToken);

                if (response.access_token) {
                    this.accessToken = response.access_token;
                }

                return createSuccessResult(response, 'Tokens refreshed successfully');

            } catch (err) {
                const errorObj = createErrorObject(err, 'Failed to refresh tokens');

                if (err.status === 401) {
                    this.clearLocalState();
                }

                return createErrorResult(errorObj, 'refresh');
            }
        },

        async executeWithTokenRotation(apiCall, options = {requireAuth: true}) {
            if (options.requireAuth && !this.accessToken) {
                throw new Error('Authentication required');
            }

            try {
                return await apiCall();
            } catch (error) {
                const statusCode = error.response?.status || error.status;

                if (statusCode === 401 && this.refreshToken) {
                    try {
                        const refreshResult = await this.refreshTokens();

                        if (refreshResult.success) {
                            return await apiCall();
                        } else {
                            await this.logout();
                            throw new Error('Your session has expired. Please log in again.');
                        }
                    } catch (refreshError) {
                        await this.logout();
                        throw new Error('Your session has expired. Please log in again.');
                    }
                }

                throw error;
            }
        },

        async changePassword(passwordData) {
            return await this.executeWithTokenRotation(
                () => accountService.changePassword(passwordData),
                {requireAuth: true}
            );
        },

        clearRegistrationState() {
            this.registrationError = null;
            this.registrationSuccess = false;
            this.registrationLoading = false;
        },

        clearLoginState() {
            this.loginError = null;
            this.loginSuccess = false;
            this.loginLoading = false;
        },

        clearActivationState() {
            this.activationError = null;
            this.activationSuccess = false;
            this.activationLoading = false;
        },

        clearResendState() {
            this.resendError = null;
            this.resendSuccess = false;
            this.resendLoading = false;
        },

        clearLogoutState() {
            this.logoutError = null;
            this.logoutLoading = false;
        },

        clearUserState() {
            this.userError = null;
            this.userLoading = false;
        },

        clearSocialAuthState() {
            this.socialAuthError = null;
            this.socialAuthSuccess = false;
            this.socialAuthLoading = false;
            this.socialAuthResult = null;
        },

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
    },

    persist: [
        {
            key: 'auth-tokens',
            storage: localStorage,
            paths: ['accessToken', 'refreshToken', 'isAuthenticated']
        },
        {
            key: 'user-data',
            storage: localStorage,
            paths: ['currentUser']
        }
    ]
});
