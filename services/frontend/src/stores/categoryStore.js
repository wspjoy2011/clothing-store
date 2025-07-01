import {defineStore} from 'pinia';
import {nextTick} from 'vue';

import categoryService from "@/services/categoryService.js";
import router from '@/router';
import {createSlug} from './helpers';

/**
 * Initial state factory for category store
 * @returns {Object} - Initial state object
 */
function createInitialCategoryState() {
    return {
        categories: [],
        loading: false,
        error: null,
        categoryMenuOpen: false,
        mobileDrawerOpen: false,

        availableFilters: {
            gender: null,
            year: null
        },
        activeFilters: {
            gender: null,
            min_year: null,
            max_year: null
        },
        filtersLoading: false,
        filtersError: null,
        isFilterDrawerOpen: false,
        isUpdatingFilters: false,
        searchQuery: null
    };
}

export const useCategoryStore = defineStore('category', {
    state: () => createInitialCategoryState(),

    getters: {
        hasCategories: (state) => state.categories.length > 0,

        activeFiltersCount() {
            let count = 0;

            if (this.activeFilters.gender !== null) {
                count++;
            }

            if (
                this.availableFilters?.year &&
                ((this.activeFilters.min_year !== null &&
                        this.activeFilters.min_year !== this.availableFilters.year.min) ||
                    (this.activeFilters.max_year !== null &&
                        this.activeFilters.max_year !== this.availableFilters.year.max))
            ) {
                count++;
            }

            return count;
        },

        hasActiveFilters() {
            return this.activeFiltersCount > 0;
        },

        getMasterCategory: (state) => (id) => {
            if (!id) return null;
            return state.categories.find(cat => cat.id.toString() === id.toString());
        },

        getMasterCategorySlug: (state) => (id) => {
            const category = state.categories.find(cat => cat.id.toString() === id.toString());
            return category ? createSlug(category.name) : '';
        },

        getMasterCategoryIdBySlug: (state) => (slug) => {
            if (!slug) return null;
            const category = state.categories.find(cat => createSlug(cat.name) === slug);
            return category ? category.id : null;
        },

        getSubCategory: (state) => (masterId, subId) => {
            if (!masterId || !subId) return null;
            const master = state.categories.find(cat => cat.id.toString() === masterId.toString());
            if (!master || !master.sub_categories) return null;

            return master.sub_categories.find(sub => sub.id.toString() === subId.toString());
        },

        getSubCategorySlug: (state) => (masterId, subId) => {
            if (!masterId || !subId) return '';
            const master = state.categories.find(cat => cat.id.toString() === masterId.toString());
            if (!master || !master.sub_categories) return '';

            const sub = master.sub_categories.find(sub => sub.id.toString() === subId.toString());
            return sub ? createSlug(sub.name) : '';
        },

        getSubCategoryIdBySlug: (state) => (masterId, slug) => {
            if (!masterId || !slug) return null;
            const master = state.categories.find(cat => cat.id.toString() === masterId.toString());
            if (!master || !master.sub_categories) return null;

            const sub = master.sub_categories.find(sub => createSlug(sub.name) === slug);
            return sub ? sub.id : null;
        },

        getArticleType: (state) => (masterId, subId, articleId) => {
            if (!masterId || !subId || !articleId) return null;
            const master = state.categories.find(cat => cat.id.toString() === masterId.toString());
            if (!master || !master.sub_categories) return null;

            const sub = master.sub_categories.find(sub => sub.id.toString() === subId.toString());
            if (!sub || !sub.article_types) return null;

            return sub.article_types.find(art => art.id.toString() === articleId.toString());
        },

        getArticleTypeSlug: (state) => (masterId, subId, articleId) => {
            if (!masterId || !subId || !articleId) return '';
            const master = state.categories.find(cat => cat.id.toString() === masterId.toString());
            if (!master || !master.sub_categories) return '';

            const sub = master.sub_categories.find(sub => sub.id.toString() === subId.toString());
            if (!sub || !sub.article_types) return '';

            const article = sub.article_types.find(art => art.id.toString() === articleId.toString());
            return article ? createSlug(article.name) : '';
        },

        getArticleTypeIdBySlug: (state) => (masterId, subId, slug) => {
            if (!masterId || !subId || !slug) return null;
            const master = state.categories.find(cat => cat.id.toString() === masterId.toString());
            if (!master || !master.sub_categories) return null;

            const sub = master.sub_categories.find(sub => sub.id.toString() === subId.toString());
            if (!sub || !sub.article_types) return null;

            const article = sub.article_types.find(art => createSlug(art.name) === slug);
            return article ? article.id : null;
        },

        getCategoryName: (state) => (masterId, subId, articleId) => {
            if (!masterId) return 'Category';

            const master = state.categories.find(cat => cat.id.toString() === masterId.toString());
            if (!master) return 'Category';

            if (!subId) return master.name;

            const sub = master.sub_categories?.find(sub => sub.id.toString() === subId.toString());
            if (!sub) return master.name;

            if (!articleId) return sub.name;

            const article = sub.article_types?.find(art => art.id.toString() === articleId.toString());
            return article ? article.name : sub.name;
        },

        getCategoryDescription: (state) => (masterId, subId, articleId) => {
            if (!masterId) return '';

            const master = state.categories.find(cat => cat.id.toString() === masterId.toString());
            if (!master) return '';

            if (!subId) return master.description || '';

            const sub = master.sub_categories?.find(sub => sub.id.toString() === subId.toString());
            if (!sub) return master.description || '';

            if (!articleId) return sub.description || '';

            const article = sub.article_types?.find(art => art.id.toString() === articleId.toString());
            return article ? (article.description || '') : (sub.description || '');
        },

        getCategoryPath: (state) => (masterId, subId, articleId) => {
            const result = [];

            if (!masterId) return result;

            const master = state.categories.find(cat => cat.id.toString() === masterId.toString());
            if (!master) return result;

            result.push({
                id: master.id,
                name: master.name,
                type: 'master',
                slug: createSlug(master.name)
            });

            if (!subId) return result;

            const sub = master.sub_categories?.find(sub => sub.id.toString() === subId.toString());
            if (!sub) return result;

            result.push({
                id: sub.id,
                name: sub.name,
                type: 'sub',
                parentId: master.id,
                slug: createSlug(sub.name)
            });

            if (!articleId) return result;

            const article = sub.article_types?.find(art => art.id.toString() === articleId.toString());
            if (!article) return result;

            result.push({
                id: article.id,
                name: article.name,
                type: 'article',
                parentId: sub.id,
                grandParentId: master.id,
                slug: createSlug(article.name)
            });

            return result;
        }
    },

    actions: {
        async fetchCategoryMenu() {
            if (this.categories.length > 0 && !this.loading) {
                return;
            }

            this.loading = true;
            this.error = null;

            try {
                const response = await categoryService.getCategoryMenu();
                this.categories = response.categories || [];
            } catch (error) {
                this.error = error.message || 'Failed to load categories';
            } finally {
                this.loading = false;
            }
        },

        async fetchCategoryFilters(masterId, subId = null, articleId = null) {
            this.filtersLoading = true;
            this.filtersError = null;

            try {
                const filters = await categoryService.getFiltersByCategory(
                    masterId,
                    subId,
                    articleId
                );
                this.availableFilters = filters || {gender: null, year: null};
            } catch (err) {
                this.filtersError = err;
                this.availableFilters = {gender: null, year: null};
            } finally {
                this.filtersLoading = false;
            }
        },

        setFilter(filterType, value) {
            if (this.isUpdatingFilters) return;

            if (filterType === 'year' && value) {
                this.activeFilters.min_year = value[0];
                this.activeFilters.max_year = value[1];
            } else if (filterType === 'gender') {
                this.activeFilters.gender = value;
            }
        },

        clearFilters() {
            const drawerWasOpen = this.isFilterDrawerOpen;

            this.isUpdatingFilters = true;

            this.activeFilters = {
                gender: null,
                min_year: null,
                max_year: null
            };

            nextTick(() => {
                this.isUpdatingFilters = false;

                if (drawerWasOpen) {
                    setTimeout(() => {
                        this.isFilterDrawerOpen = true;
                    }, 0);
                }
            });
        },

        clearSearch() {
            this.searchQuery = null;
        },

        setSearchQuery(query) {
            this.searchQuery = query?.trim() || null;
        },

        loadFiltersFromQuery(query) {
            this.isUpdatingFilters = true;

            this.activeFilters = {
                gender: null,
                min_year: null,
                max_year: null
            };

            if (query.gender) {
                this.activeFilters.gender = query.gender;
            }

            if (query.min_year) {
                this.activeFilters.min_year = parseInt(query.min_year);
            }

            if (query.max_year) {
                this.activeFilters.max_year = parseInt(query.max_year);
            }

            this.searchQuery = query.q?.trim() || null;

            nextTick(() => {
                this.isUpdatingFilters = false;
            });
        },

        toggleFilterDrawer(value = null) {
            if (value !== null) {
                this.isFilterDrawerOpen = value;
            } else {
                this.isFilterDrawerOpen = !this.isFilterDrawerOpen;
            }
        },

        resetCategoryFilters() {
            this.availableFilters = {
                gender: null,
                year: null
            };
            this.activeFilters = {
                gender: null,
                min_year: null,
                max_year: null
            };
            this.filtersError = null;
            this.isFilterDrawerOpen = false;
            this.searchQuery = null;
            this.isUpdatingFilters = false;
        },

        closeMenus() {
            this.categoryMenuOpen = false;
            this.mobileDrawerOpen = false;
        },

        navigateToCategory(categoryInfo) {
            this.closeMenus();

            if (!categoryInfo || !categoryInfo.type || !categoryInfo.id) {
                return;
            }

            const {type, id, name} = categoryInfo;
            const slug = createSlug(name);

            if (type === 'master') {
                router.push({
                    name: 'master-category',
                    params: {masterCategory: slug}
                });
            } else if (type === 'sub') {
                const parentId = categoryInfo.parentId;
                if (!parentId) {
                    return;
                }

                const masterCategory = this.getMasterCategory(parentId);
                if (!masterCategory) {
                    return;
                }

                router.push({
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

                const masterCategory = this.getMasterCategory(grandParentId);
                if (!masterCategory) {
                    return;
                }

                const subCategory = this.getSubCategory(grandParentId, parentId);
                if (!subCategory) {
                    return;
                }

                router.push({
                    name: 'article-type',
                    params: {
                        masterCategory: createSlug(masterCategory.name),
                        subCategory: createSlug(subCategory.name),
                        articleType: slug
                    }
                });
            }
        },

        /**
         * Reset category store to initial state
         */
        resetState() {
            Object.assign(this.$state, createInitialCategoryState());
        }
    }
});
