import {createSlug} from './slugUtils.js';

/**
 * Find category tree elements by IDs
 * @param {Array} categories - Array of categories
 * @param {string|number} masterId - Master category ID
 * @param {string|number} subId - Sub category ID (optional)
 * @param {string|number} articleId - Article type ID (optional)
 * @returns {Object} - Object containing master, sub, and article references
 */
export function findCategoryTree(categories, masterId, subId, articleId) {
    const master = masterId ? categories.find(cat => cat.id.toString() === masterId.toString()) : null;
    const sub = (master?.sub_categories && subId) ?
        master.sub_categories.find(sc => sc.id.toString() === subId.toString()) : null;
    const article = (sub?.article_types && articleId) ?
        sub.article_types.find(a => a.id.toString() === articleId.toString()) : null;

    return {master, sub, article};
}

/**
 * Find category by slug
 * @param {Array} categories - Array of categories
 * @param {string} slug - Category slug
 * @returns {Object|null} - Found category or null
 */
export function findCategoryBySlug(categories, slug) {
    if (!slug) return null;
    return categories.find(cat => createSlug(cat.name) === slug);
}

/**
 * Find sub-category by slug within master category
 * @param {Object} masterCategory - Master category object
 * @param {string} slug - Sub-category slug
 * @returns {Object|null} - Found sub-category or null
 */
export function findSubCategoryBySlug(masterCategory, slug) {
    if (!masterCategory?.sub_categories || !slug) return null;
    return masterCategory.sub_categories.find(sub => createSlug(sub.name) === slug);
}

/**
 * Find article type by slug within sub-category
 * @param {Object} subCategory - Sub-category object
 * @param {string} slug - Article type slug
 * @returns {Object|null} - Found article type or null
 */
export function findArticleTypeBySlug(subCategory, slug) {
    if (!subCategory?.article_types || !slug) return null;
    return subCategory.article_types.find(art => createSlug(art.name) === slug);
}
