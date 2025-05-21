<template>
  <div class="category-menu">
    <div v-if="isLoading" class="d-flex justify-center pa-4">
      <v-progress-circular indeterminate color="primary" />
    </div>

    <div v-else-if="hasError" class="text-center text-error pa-4">
      {{ hasError }}
    </div>

    <div v-else-if="!categoriesExist" class="text-center pa-4">
      No categories available
    </div>

    <div v-else class="category-menu-container">
      <category-menu-item
        v-for="category in categoriesData"
        :key="`category-${category.id}`"
        :item="category"
        @item-click="handleCategoryClick"
      />
    </div>
  </div>
</template>

<script>
import { mapActions } from 'pinia';
import { useCategoryStore } from '@/stores/categoryStore';
import CategoryMenuItem from './CategoryMenuItem.vue';

export default {
  name: 'CategoryMenu',

  components: {
    CategoryMenuItem
  },

  props: {
    propCategories: {
      type: Array,
      default: null
    },
    propLoading: {
      type: Boolean,
      default: null
    },
    propError: {
      type: [String, Object],
      default: null
    },
    propHasCategories: {
      type: Boolean,
      default: null
    },
    onCategoryClick: {
      type: Function,
      default: null
    }
  },

  data() {
    return {
      storeCategories: [],
      storeLoading: false,
      storeError: null
    };
  },

  computed: {
    categoriesData() {
      return this.propCategories !== null ? this.propCategories : this.storeCategories;
    },

    isLoading() {
      return this.propLoading !== null ? this.propLoading : this.storeLoading;
    },

    hasError() {
      return this.propError !== null ? this.propError : this.storeError;
    },

    categoriesExist() {
      return this.propHasCategories !== null ? this.propHasCategories : this.storeCategories.length > 0;
    }
  },

  methods: {
    ...mapActions(useCategoryStore, ['fetchCategoryMenu']),

    handleCategoryClick(categoryInfo) {
      console.log('Category clicked:', categoryInfo);

      if (this.onCategoryClick) {
        this.onCategoryClick(categoryInfo);
      } else {
        this.$emit('category-select', categoryInfo);
      }
    },

    async loadFromStore() {
      const store = useCategoryStore();
      this.storeLoading = true;

      try {
        await store.fetchCategoryMenu();
        this.storeCategories = store.categories;
        this.storeError = store.error;
      } catch (error) {
        this.storeError = error.message || 'Failed to load categories';
      } finally {
        this.storeLoading = false;
      }
    }
  },

  created() {
    if (this.propCategories === null && !this.propHasCategories && !this.propLoading) {
      this.loadFromStore();
    }
  }
}
</script>

<style scoped>
.category-menu {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

.category-menu-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 8px;
  padding: 16px;
  max-width: 800px;
}

@media (max-width: 600px) {
  .category-menu-container {
    grid-template-columns: 1fr;
  }
}

.category-menu-container > * {
  transition: transform 0.2s ease, opacity 0.2s ease;
}

.category-menu-container > *:hover {
  transform: translateY(-2px);
}
</style>
