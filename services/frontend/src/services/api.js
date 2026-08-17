import axios from 'axios';

const API_CONFIG = {
    baseURL: import.meta.env.VITE_API_BASE_URL,
    timeout: 10000,
    headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }
};

const api = axios.create(API_CONFIG);

const getAccessToken = () => {
    try {
        const authTokens = localStorage.getItem('auth-tokens');
        if (authTokens) {
            const tokens = JSON.parse(authTokens);
            return tokens.accessToken;
        }
        return null;
    } catch (error) {
        return null;
    }
};

const getRefreshToken = () => {
    try {
        const authTokens = localStorage.getItem('auth-tokens');
        if (authTokens) {
            const tokens = JSON.parse(authTokens);
            return tokens.refreshToken;
        }
        return null;
    } catch (error) {
        return null;
    }
};

/**
 * Store a freshly issued token pair
 *
 * The refresh token is replaced on every refresh: the server invalidates the one
 * that was presented, so keeping the old one would log the user out on the next
 * refresh.
 *
 * @param {string} newAccessToken - Access token to use from now on
 * @param {string} newRefreshToken - Refresh token replacing the presented one
 * @returns {void}
 */
const updateTokens = (newAccessToken, newRefreshToken) => {
    try {
        const authTokens = localStorage.getItem('auth-tokens');
        if (authTokens) {
            const tokens = JSON.parse(authTokens);
            tokens.accessToken = newAccessToken;
            tokens.refreshToken = newRefreshToken;
            localStorage.setItem('auth-tokens', JSON.stringify(tokens));
        }
    } catch (error) {
        console.error('Failed to update tokens:', error);
    }
};

let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
    failedQueue.forEach(prom => {
        if (error) {
            prom.reject(error);
        } else {
            prom.resolve(token);
        }
    });
    failedQueue = [];
};

const addToQueue = () => {
    return new Promise((resolve, reject) => {
        failedQueue.push({resolve, reject});
    });
};

const refreshAccessToken = async () => {
    const refreshToken = getRefreshToken();

    if (!refreshToken) {
        throw new Error('No refresh token available');
    }

    console.log('Attempting to refresh tokens...');

    const refreshResponse = await axios.post(
        `${API_CONFIG.baseURL}/accounts/refresh`,
        {refresh_token: refreshToken},
        {
            headers: API_CONFIG.headers,
            timeout: API_CONFIG.timeout
        }
    );

    if (!refreshResponse.data.access_token || !refreshResponse.data.refresh_token) {
        throw new Error('Incomplete token pair in refresh response');
    }

    const newAccessToken = refreshResponse.data.access_token;
    updateTokens(newAccessToken, refreshResponse.data.refresh_token);

    console.log('Tokens refreshed successfully');
    return newAccessToken;
};


const handleExpiredRefreshToken = async () => {
    try {
        console.log('Performing logout due to expired refresh token');

        const {useAccountStore} = await import('@/stores/accounts.js');
        const {useCartStore} = await import('@/stores/cart.js');
        const {createSuccessResult} = await import('@/stores/helpers/apiErrorParser.js');
        const router = await import('@/router/index.js');

        const accountStore = useAccountStore();
        const cartStore = useCartStore();

        accountStore.clearLocalState();

        cartStore.resetInitialization();
        await cartStore.initializeCart();

        console.log('User logged out and cart reinitialized as anonymous');

        router.default.push({
            name: 'login',
            query: {
                next: router.default.currentRoute.value.fullPath,
                reason: 'session_expired'
            }
        });

        return createSuccessResult(
            null,
            'Session expired. You have been logged out automatically.'
        );

    } catch (logoutError) {
        console.error('Error during logout process:', logoutError);
        throw logoutError;
    }
};

const createApiError = (response) => {
    const status = response?.status || 500;
    const detail = response?.data?.detail || response?.data?.message;

    const errorMap = {
        400: detail || 'Invalid request data',
        401: detail || 'Unauthorized',
        403: detail || 'Access forbidden',
        404: detail || 'Resource not found',
        409: detail || 'Resource already exists',
        422: response?.data?.message || 'Validation error',
        500: detail || 'Server request error'
    };

    return {
        status,
        message: errorMap[status] || detail || 'Unknown error',
        field: response?.data?.field
    };
};

const handleApiError = (error) => {
    return Promise.reject(createApiError(error.response));
};

api.interceptors.request.use(
    (config) => {
        if (config.url && config.url.includes('/accounts/me')) {
            const refreshToken = getRefreshToken();
            if (refreshToken) {
                config.headers.Authorization = `Bearer ${refreshToken}`;
            }
        } else {
            const accessToken = getAccessToken();
            if (accessToken) {
                config.headers.Authorization = `Bearer ${accessToken}`;
            }
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

api.interceptors.response.use(
    response => response,
    async error => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && !originalRequest._retry) {
            if (originalRequest.url?.includes('/accounts/refresh') ||
                originalRequest.url?.includes('/accounts/logout')) {
                return handleApiError(error);
            }

            if (isRefreshing) {
                try {
                    const token = await addToQueue();
                    if (token) {
                        originalRequest.headers['Authorization'] = 'Bearer ' + token;
                        return api(originalRequest);
                    }
                } catch (queueError) {
                    return Promise.reject(queueError);
                }
            }

            originalRequest._retry = true;
            isRefreshing = true;

            try {
                const newAccessToken = await refreshAccessToken();

                processQueue(null, newAccessToken);

                originalRequest.headers['Authorization'] = 'Bearer ' + newAccessToken;
                return api(originalRequest);

            } catch (refreshError) {
                console.error('Token refresh failed:', refreshError);

                processQueue(refreshError, null);

                await handleExpiredRefreshToken();

                throw new Error('Session expired, user logged out');
            } finally {
                isRefreshing = false;
            }
        }

        return handleApiError(error);
    }
);

export default api;
