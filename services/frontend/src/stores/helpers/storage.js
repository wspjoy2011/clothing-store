/**
 * LocalStorage helper utilities
 */
export const storage = {
    /**
     * Get value from localStorage
     * @param {string} key - Storage key
     * @returns {string|null} - Retrieved value or null
     */
    get(key) {
        try {
            return localStorage.getItem(key);
        } catch (error) {
            console.warn(`Failed to get item from localStorage: ${key}`, error);
            return null;
        }
    },

    /**
     * Set value in localStorage
     * @param {string} key - Storage key
     * @param {string} value - Value to store
     */
    set(key, value) {
        try {
            localStorage.setItem(key, value);
        } catch (error) {
            console.warn(`Failed to set item in localStorage: ${key}`, error);
        }
    },

    /**
     * Remove one or more keys from localStorage
     * @param {...string} keys - Keys to remove
     */
    remove(...keys) {
        keys.forEach(key => {
            try {
                localStorage.removeItem(key);
            } catch (error) {
                console.warn(`Failed to remove item from localStorage: ${key}`, error);
            }
        });
    },

    /**
     * Clear all localStorage data
     */
    clear() {
        try {
            localStorage.clear();
        } catch (error) {
            console.warn('Failed to clear localStorage', error);
        }
    }
};
