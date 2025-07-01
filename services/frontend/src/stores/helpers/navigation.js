import router from '@/router';
import {createSlug} from './slugUtils.js';

/**
 * Navigate to category based on category information
 * @param {Object} categoryInfo - Category information object
 * @param {string} categoryInfo.type - Category type ('master', 'sub', 'article')
 * @param {string|number} categoryInfo.id - Category ID
 * @param {string} categoryInfo.name - Category name
 * @param {string|number} [categoryInfo.parentId] - Parent category ID (for sub and article)
 * @param {string|number} [categoryInfo.grandParentId] - Grand parent category ID (for article)
 * @param {Object} store - Category store instance
 * @returns {Promise<void>}
 */
export async function navigateToCategory(categoryInfo, store) {
    if (!categoryInfo || !categoryInfo.type || !categoryInfo.id) {
        return;
    }

    const {type, name} = categoryInfo;
    const slug = createSlug(name);

    try {
        if (type === 'master') {
            await router.push({
                name: 'master-category',
                params: {masterCategory: slug}
            });
        } else if (type === 'sub') {
            const parentId = categoryInfo.parentId;
            if (!parentId) {
                return;
            }

            const masterCategory = store.getMasterCategory(parentId);
            if (!masterCategory) {
                return;
            }

            await router.push({
                name: 'sub-category',
                params: {
                    masterCategory: createSlug(masterCategory.name),
                    subCategory: slug
                }
            });
        } else if (type === 'article') {
            const parentId = categoryInfo.parentId;
            const grandParentId = categoryInfo.grandParentId;

            if (!parentId || !grandParentId) {
                return;
            }

            const masterCategory = store.getMasterCategory(grandParentId);
            if (!masterCategory) {
                return;
            }

            const subCategory = store.getSubCategory(grandParentId, parentId);
            if (!subCategory) {
                return;
            }

            await router.push({
                name: 'article-type',
                params: {
                    masterCategory: createSlug(masterCategory.name),
                    subCategory: createSlug(subCategory.name),
                    articleType: slug
                }
            });
        }
    } catch (error) {
        throw error;
    }
}

/**
 * Generate category route parameters
 * @param {Object} categoryInfo - Category information object
 * @param {Object} store - Category store instance
 * @returns {Object|null} - Route object or null if invalid
 */
export function getCategoryRoute(categoryInfo, store) {
    if (!categoryInfo || !categoryInfo.type || !categoryInfo.id) {
        return null;
    }

    const {type, name} = categoryInfo;
    const slug = createSlug(name);

    if (type === 'master') {
        return {
            name: 'master-category',
            params: {masterCategory: slug}
        };
    } else if (type === 'sub') {
        const parentId = categoryInfo.parentId;
        if (!parentId) return null;

        const masterCategory = store.getMasterCategory(parentId);
        if (!masterCategory) return null;

        return {
            name: 'sub-category',
            params: {
                masterCategory: createSlug(masterCategory.name),
                subCategory: slug
            }
        };
    } else if (type === 'article') {
        const parentId = categoryInfo.parentId;
        const grandParentId = categoryInfo.grandParentId;

        if (!parentId || !grandParentId) return null;

        const masterCategory = store.getMasterCategory(grandParentId);
        if (!masterCategory) return null;

        const subCategory = store.getSubCategory(grandParentId, parentId);
        if (!subCategory) return null;

        return {
            name: 'article-type',
            params: {
                masterCategory: createSlug(masterCategory.name),
                subCategory: createSlug(subCategory.name),
                articleType: slug
            }
        };
    }

    return null;
}

/**
 * Build breadcrumb navigation items from category path
 * @param {Array} categoryPath - Array of category path items
 * @returns {Array} - Array of breadcrumb items
 */
export function buildBreadcrumbs(categoryPath) {
    return categoryPath.map((item, index) => ({
        text: item.name,
        disabled: index === categoryPath.length - 1,
        href: index === categoryPath.length - 1 ? undefined : `#${item.slug}`,
        exact: true
    }));
}
