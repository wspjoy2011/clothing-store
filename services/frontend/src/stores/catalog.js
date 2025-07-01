import {defineStore} from 'pinia'

import catalogService from '@/services/catalogService'
import {useUserPreferencesStore} from '@/stores/userPreferences'
import {
    createInitialFiltersState,
    createFiltersGetters,
    createFiltersActions
} from './composables';

/**
 * Initial state factory for catalog store
 * @returns {Object} - Initial state object
 */
function createInitialCatalogState() {
    return {
        products: [],
        currentPage: 1,
        totalPages: 0,
        totalItems: 0,
        currentOrdering: '-id',
        loading: false,
        error: null,

        currentProduct: null,
        productLoading: false,
        productError: null,

        ...createInitialFiltersState()
    };
}

export const useCatalogStore = defineStore('catalog', {
    state: () => createInitialCatalogState(),

    getters: {
        ...createFiltersGetters(),

        getProductIdBySlug: (state) => (slug) => {
            if (!slug) return null;
            const product = state.products.find(p => p.slug === slug);
            return product ? product.product_id : null;
        },

        getProductSlugById: (state) => (productId) => {
            if (!productId) return null;
            const product = state.products.find(p => p.product_id === productId);
            return product ? product.slug : null;
        },

        hasProductById: (state) => (productId) => {
            if (!productId) return false;
            return state.products.some(p => p.product_id === productId);
        }
    },

    actions: {
        async fetchProducts(page = 1, ordering = null) {
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

                const response = await catalogService.getProducts(
                    page,
                    perPage,
                    effectiveOrdering,
                    filters
                );

                this.products = response.products;
                this.totalPages = response.total_pages;
                this.totalItems = response.total_items;
                this.currentPage = page;
                this.currentOrdering = effectiveOrdering;
            } catch (err) {
                this.error = err.response?.data || {message: 'Error loading products'};
                this.products = [];
            } finally {
                this.loading = false;
            }
        },

        async fetchProductById(productId) {
            this.productLoading = true;
            this.productError = null;

            try {
                const product = await catalogService.getProductById(productId);
                this.currentProduct = product;
                return product;
            } catch (err) {
                this.productError = err.response?.data || {message: 'Error loading product'};
                this.currentProduct = null;
                throw err;
            } finally {
                this.productLoading = false;
            }
        },

        async fetchProductBySlug(slug) {
            this.productLoading = true;
            this.productError = null;

            try {
                const product = await catalogService.getProductBySlug(slug);
                this.currentProduct = product;
                return product;
            } catch (err) {
                this.productError = err.response?.data || {message: 'Error loading product'};
                this.currentProduct = null;
                throw err;
            } finally {
                this.productLoading = false;
            }
        },

        async getProductById(productId) {
            if (this.currentProduct && this.currentProduct.product_id === productId) {
                return this.currentProduct;
            }

            const existingProduct = this.products.find(p => p.product_id === productId);
            if (existingProduct) {
                this.currentProduct = existingProduct;
                return existingProduct;
            }

            return await this.fetchProductById(productId);
        },

        async getProductBySlug(slug) {
            if (this.currentProduct && this.currentProduct.slug === slug) {
                return this.currentProduct;
            }

            const existingProduct = this.products.find(p => p.slug === slug);
            if (existingProduct) {
                this.currentProduct = existingProduct;
                return existingProduct;
            }

            return await this.fetchProductBySlug(slug);
        },

        async fetchFilters() {
            this.filtersLoading = true;
            this.filtersError = null;

            try {
                this.availableFilters = await catalogService.getFilters(this.searchQuery);
            } catch (err) {
                this.filtersError = err.response?.data || {message: 'Error loading filters'};
                this.availableFilters = {gender: null, year: null};
            } finally {
                this.filtersLoading = false;
            }
        },

        ...createFiltersActions(),

        setOrdering(ordering) {
            if (ordering !== this.currentOrdering) {
                this.currentOrdering = ordering;
            }
        },

        clearCurrentProduct() {
            this.currentProduct = null;
            this.productError = null;
        },

        /**
         * Reset catalog store to initial state
         */
        resetState() {
            Object.assign(this.$state, createInitialCatalogState());
        }
    }
});
