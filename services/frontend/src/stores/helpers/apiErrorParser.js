/**
 * Parse API errors and return user-friendly messages
 * @param {Object} error - Error object with status and message
 * @param {string} type - Error type for specific message mapping
 * @returns {string} - User-friendly error message
 */
export function parseApiError(error, type = 'default') {
    const fallbackMessages = {
        registration: 'Registration failed. Please try again.',
        login: 'Login failed. Please try again.',
        activation: 'Account activation failed. Please try again.',
        resend: 'Failed to send activation email. Please try again.',
        logout: 'Logout failed. Please try again.',
        user: 'Failed to load user data.',
        social: 'Social authentication failed. Please try again.',
        default: 'Unexpected error. Please try again.',
    };

    if (!error) {
        return fallbackMessages[type] || fallbackMessages.default;
    }

    const status = error?.status;
    const message = error?.message;

    const messagesByType = {
        registration: {
            400: 'Invalid registration data. Please check your information and try again.',
            409: 'This email address is already registered. Please use a different email or try signing in.',
            422: 'Please check your input data',
            500: 'Server error. Please try again later.',
        },
        login: {
            400: 'Invalid login credentials. Please check your email and password.',
            403: 'Account not activated. Please check your email for activation instructions.',
            404: 'User not found. Please check your credentials or register a new account.',
            422: 'Please check your input data',
            500: 'Server error. Please try again later.',
        },
        activation: {
            400: 'Invalid activation data or account already activated.',
            404: 'User not found. Please check your email address.',
            410: 'Activation token has expired. Please request a new activation email.',
            422: 'Invalid activation link format.',
            500: 'Server error. Please try again later.',
        },
        resend: {
            400: 'This account is already activated or invalid request.',
            404: 'User not found. Please check your email address.',
            422: 'Please enter a valid email address.',
            500: 'Server error. Please try again later.',
        },
        logout: {
            400: 'Invalid logout request.',
            401: 'Unauthorized logout attempt.',
            500: 'Server error during logout. Please try again later.',
        },
        user: {
            401: 'Session expired. Please login again.',
            404: 'User not found.',
            500: 'Server error. Please try again later.',
        },
        social: {
            400: 'Invalid social authentication request',
            401: 'Invalid access token from social provider',
            422: 'Validation error during social authentication',
            503: 'Social authentication service temporarily unavailable',
            500: 'Server error during social authentication. Please try again later.',
        },
        default: {
            500: 'Server error. Please try again later.',
            404: 'Resource not found.',
            403: 'Access denied.',
            401: 'Authentication required.',
            400: 'Bad request.',
        }
    };

    if (message) {
        if (status === 422 && error.field) {
            return `${error.field}: ${message}`;
        }
        return message;
    }

    const typeMessages = messagesByType[type];
    if (typeMessages && typeMessages[status]) {
        return typeMessages[status];
    }

    const defaultMessages = messagesByType.default;
    if (defaultMessages[status]) {
        return defaultMessages[status];
    }

    return fallbackMessages[type] || fallbackMessages.default;
}

/**
 * Check if error indicates specific conditions
 * @param {Object} error - Error object
 * @param {string} condition - Condition to check
 * @returns {boolean} - Whether condition is met
 */
export function checkErrorCondition(error, condition) {
    const status = error?.status;

    const conditions = {
        needsActivation: status === 403,
        needsRegistration: status === 404,
        sessionExpired: status === 401,
        tokenExpired: status === 410,

        emailAlreadyExists: status === 409,

        validationError: status === 422,

        serverError: status >= 500,
        clientError: status >= 400 && status < 500,
    };

    return conditions[condition] || false;
}

/**
 * Create standardized error object
 * @param {Object} err - Raw error from API
 * @param {string} defaultMessage - Default message if none provided
 * @returns {Object} - Standardized error object
 */
export function createErrorObject(err, defaultMessage = 'Operation failed') {
    return {
        status: err?.status || 500,
        message: err?.message || defaultMessage,
        field: err?.field || null,
        code: err?.code || null,
    };
}

/**
 * Create standardized success result
 * @param {Object} data - Response data
 * @param {string} message - Success message
 * @returns {Object} - Standardized success result
 */
export function createSuccessResult(data, message) {
    return {
        success: true,
        data,
        message: data?.message || message,
    };
}

/**
 * Create standardized error result
 * @param {Object} error - Error object
 * @param {string} type - Error type for message parsing
 * @returns {Object} - Standardized error result
 */
export function createErrorResult(error, type = 'default') {
    return {
        success: false,
        error,
        message: parseApiError(error, type),
    };
}
