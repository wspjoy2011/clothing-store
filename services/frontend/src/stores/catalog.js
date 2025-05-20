import { defineStore } from 'pinia'
import catalogService from '@/services/catalogService'
import { useUserPreferencesStore } from '@/stores/userPreferences'
import { nextTick } from 'vue'

export const useCatalogStore = defineStore('catalog', {
  state: () => ({
    products: [],
    currentPage: 1,
    totalPages: 0,
    totalItems: 0,
    currentOrdering: '-id',
    loading: false,
    error: null,

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
  }),

  getters: {
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
        this.error = err.response?.data || { message: 'Error loading products' };
        this.products = [];
      } finally {
        this.loading = false;
      }
    },

    async fetchFilters() {
      this.filtersLoading = true;
      this.filtersError = null;

      try {
        const filters = await catalogService.getFilters(this.searchQuery);
        this.availableFilters = filters;
      } catch (err) {
        this.filtersError = err.response?.data || { message: 'Error loading filters' };
        this.availableFilters = { gender: null, year: null };
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
      this.searchQuery = query && query.trim() ? query.trim() : null;
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

      if (query.q) {
        this.searchQuery = query.q;
      } else {
        this.searchQuery = null;
      }

      nextTick(() => {
        this.isUpdatingFilters = false;
      });
    },

    setOrdering(ordering) {
      if (ordering !== this.currentOrdering) {
        this.currentOrdering = ordering;
      }
    },

    toggleFilterDrawer(value = null) {
      if (value !== null) {
        this.isFilterDrawerOpen = value;
      } else {
        this.isFilterDrawerOpen = !this.isFilterDrawerOpen;
      }
    },

    resetState() {
      this.products = [];
      this.currentPage = 1;
      this.totalPages = 0;
      this.totalItems = 0;
      this.currentOrdering = '-id';
      this.error = null;
      this.isFilterDrawerOpen = false;
      this.searchQuery = null;

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
      this.isUpdatingFilters = false;
    }
  }
});