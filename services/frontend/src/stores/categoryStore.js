import {defineStore} from 'pinia';
import {nextTick} from 'vue';

import categoryService from "@/services/categoryService.js";
import {
    createSlug,
    findCategoryTree,
    findCategoryBySlug,
    findSubCategoryBySlug,
    findArticleTypeBySlug,
    navigateToCategory
} from './helpers';

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
            const category = findCategoryBySlug(state.categories, slug);
            return category ? category.id : null;
        },

        getSubCategory: (state) => (masterId, subId) => {
            const {sub} = findCategoryTree(state.categories, masterId, subId);
            return sub;
        },

        getSubCategorySlug: (state) => (masterId, subId) => {
            const {sub} = findCategoryTree(state.categories, masterId, subId);
            return sub ? createSlug(sub.name) : '';
        },

        getSubCategoryIdBySlug: (state) => (masterId, slug) => {
            const {master} = findCategoryTree(state.categories, masterId);
            const sub = findSubCategoryBySlug(master, slug);
            return sub ? sub.id : null;
        },

        getArticleType: (state) => (masterId, subId, articleId) => {
            const {article} = findCategoryTree(state.categories, masterId, subId, articleId);
            return article;
        },

        getArticleTypeSlug: (state) => (masterId, subId, articleId) => {
            const {article} = findCategoryTree(state.categories, masterId, subId, articleId);
            return article ? createSlug(article.name) : '';
        },

        getArticleTypeIdBySlug: (state) => (masterId, subId, slug) => {
            const {sub} = findCategoryTree(state.categories, masterId, subId);
            const article = findArticleTypeBySlug(sub, slug);
            return article ? article.id : null;
        },

        getCategoryName: (state) => (masterId, subId, articleId) => {
            const {master, sub, article} = findCategoryTree(state.categories, masterId, subId, articleId);
            return article?.name || sub?.name || master?.name || 'Category';
        },

        getCategoryDescription: (state) => (masterId, subId, articleId) => {
            const {master, sub, article} = findCategoryTree(state.categories, masterId, subId, articleId);
            return article?.description || sub?.description || master?.description || '';
        },

        getCategoryPath: (state) => (masterId, subId, articleId) => {
            const result = [];
            const {master, sub, article} = findCategoryTree(state.categories, masterId, subId, articleId);

            if (master) {
                result.push({
                    id: master.id,
                    name: master.name,
                    type: 'master',
                    slug: createSlug(master.name)
                });
            }

            if (sub) {
                result.push({
                    id: sub.id,
                    name: sub.name,
                    type: 'sub',
                    parentId: master.id,
                    slug: createSlug(sub.name)
                });
            }

            if (article) {
                result.push({
                    id: article.id,
                    name: article.name,
                    type: 'article',
                    parentId: sub.id,
                    grandParentId: master.id,
                    slug: createSlug(article.name)
                });
            }

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
            return navigateToCategory(categoryInfo, this);
        },

        /**
         * Reset category store to initial state
         */
        resetState() {
            Object.assign(this.$state, createInitialCategoryState());
        }
    }
});
