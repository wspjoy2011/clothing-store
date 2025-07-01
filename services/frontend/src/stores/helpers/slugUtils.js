
/**
 * Convert name to URL-friendly slug
 * @param {string} name - The name to convert to slug
 * @returns {string} - URL-friendly slug
 */
export function createSlug(name) {
    if (!name || typeof name !== 'string') {
        return '';
    }

    return name
        .toLowerCase()
        .replace(/[^a-z0-9]+/g, '-')
        .replace(/(^-|-$)/g, '');
}

/**
 * Convert slug back to display name (basic implementation)
 * @param {string} slug - The slug to convert
 * @returns {string} - Display name
 */
export function slugToName(slug) {
    if (!slug || typeof slug !== 'string') {
        return '';
    }

    return slug
        .split('-')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
}
