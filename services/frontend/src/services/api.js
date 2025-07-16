import axios from 'axios';

const api = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL,
    timeout: 10000,
    headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }
});

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

const handleApiError = (error) => {
    const {response} = error;

    if (response && response.status === 403) {
        return Promise.reject({
            status: response.status,
            message: response.data.detail || 'Access forbidden'
        });
    }

    if (response && response.status === 404) {
        return Promise.reject({
            status: response.status,
            message: response.data.detail || 'Resource not found'
        });
    }

    if (response && response.status === 422) {
        return Promise.reject({
            status: response.status,
            field: response.data.field,
            message: response.data.message || 'Validation error'
        });
    }

    if (response && response.status === 409) {
        return Promise.reject({
            status: response.status,
            message: response.data.detail || response.data.message || 'Resource already exists'
        });
    }

    if (response && response.status === 400) {
        return Promise.reject({
            status: response.status,
            message: response.data.detail || response.data.message || 'Invalid request data'
        });
    }

    if (response && response.status === 401) {
        return Promise.reject({
            status: response.status,
            message: response.data.detail || response.data.message || 'Unauthorized'
        });
    }

    return Promise.reject({
        status: response?.status || 500,
        message: response?.data?.detail || response?.data?.message || 'Server request error'
    });
};

api.interceptors.response.use(
    response => response,
    error => handleApiError(error)
);

export default api;
