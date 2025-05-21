import { defineStore } from 'pinia';
import categoryService from "@/services/categoryService.js";

export const useCategoryStore = defineStore('category', {
  state: () => ({
    categories: [],
    loading: false,
    error: null
  }),

  getters: {
    hasCategories: (state) => state.categories.length > 0
  },

  actions: {
    async fetchCategoryMenu() {
      this.loading = true;
      this.error = null;

      try {
        const response = await categoryService.getCategoryMenu();
        this.categories = response.categories || [];
      } catch (error) {
        this.error = error.message || 'Failed to load categories';
        console.error('Category menu fetch error:', error);
      } finally {
        this.loading = false;
      }
    }
  }
});
