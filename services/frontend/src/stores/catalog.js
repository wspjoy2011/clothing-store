import { defineStore } from 'pinia'

import catalogService from '@/services/catalogService'
import { useUserPreferencesStore } from '@/stores/userPreferences'

export const useCatalogStore = defineStore('catalog', {
  state: () => ({
    products: [],
    currentPage: 1,
    totalPages: 0,
    totalItems: 0,
    loading: false,
    error: null,
  }),

  actions: {
    async fetchProducts(page = 1) {
      this.loading = true;
      this.error = null;
      
      const preferencesStore = useUserPreferencesStore();
      const perPage = preferencesStore.itemsPerPage;

      try {
        const response = await catalogService.getProducts(page, perPage);
        this.products = response.products;
        this.totalPages = response.total_pages;
        this.totalItems = response.total_items;
        this.currentPage = page;
      } catch (err) {
        this.error = err;
        this.products = [];
      } finally {
        this.loading = false;
      }
    },
    
    resetState() {
      this.products = [];
      this.currentPage = 1;
      this.totalPages = 0;
      this.totalItems = 0;
      this.error = null;
    }
  }
});
