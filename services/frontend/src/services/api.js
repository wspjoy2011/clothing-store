import axios from 'axios';

const api = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL,
    timeout: 10000,
    headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }
});

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
