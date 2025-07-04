import {defineStore} from 'pinia';

import categoryService from "@/services/categoryService.js";
import {useUserPreferencesStore} from '@/stores/userPreferences';
import {
    createSlug,
    findCategoryTree,
    findCategoryBySlug,
    findSubCategoryBySlug,
    findArticleTypeBySlug,
    navigateToCategory
} from './helpers';
import {
    createInitialFiltersState,
    createFiltersGetters,
    createFiltersActions,
    createPaginationState,
    createPaginationActions,
    createPaginationGetters
} from './composables';

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

        products: [],
        currentOrdering: '-id',

        ...createInitialFiltersState(),
        ...createPaginationState()
    };
}

export const useCategoryStore = defineStore('category', {
    state: () => createInitialCategoryState(),

    getters: {
        hasCategories: (state) => state.categories.length > 0,

        ...createFiltersGetters(),
        ...createPaginationGetters(),

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

        async fetchProducts(page = 1, ordering = null, masterId = null, subId = null, articleId = null) {
            this.loading = true;
            this.error = null;

            const preferencesStore = useUserPreferencesStore();
            const perPage = preferencesStore.itemsPerPage;

            const effectiveOrdering = ordering !== null ? ordering : this.currentOrdering;

            try {
                const filters = {
                    ...this.activeFilters,
                    q: this.searchQuery
                };

                const response = await categoryService.getProductsByCategory(
                    masterId,
                    subId,
                    articleId,
                    page,
                    perPage,
                    effectiveOrdering,
                    filters,
                    this.searchQuery
                );

                this.products = response.products;
                this.setPaginationData({
                    currentPage: page,
                    totalPages: response.total_pages,
                    totalItems: response.total_items
                });
                this.currentOrdering = effectiveOrdering;
            } catch (err) {
                this.error = err.response?.data || {message: 'Error loading products'};
                this.products = [];
                this.resetPagination();
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

        ...createFiltersActions(),
        ...createPaginationActions(),

        setOrdering(ordering) {
            if (ordering !== this.currentOrdering) {
                this.currentOrdering = ordering;
            }
        },

        resetCategoryFilters() {
            this.resetFilters();
            this.resetPagination();
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
