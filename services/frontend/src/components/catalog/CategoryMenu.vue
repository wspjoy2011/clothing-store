<template>
  <div class="category-menu" :class="{ 'theme-dark': isDarkTheme }">
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
        class="menu-item-vertical"
      />
    </div>
  </div>
</template>

<script>
import { mapActions, mapState } from 'pinia';
import { useCategoryStore } from '@/stores/categoryStore';
import { useTheme } from 'vuetify';
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
    ...mapState(useCategoryStore, ['categories']),
    
    categoriesData() {
      return this.propCategories !== null ? this.propCategories : this.categories;
    },

    isLoading() {
      return this.propLoading !== null ? this.propLoading : this.storeLoading;
    },

    hasError() {
      return this.propError !== null ? this.propError : this.storeError;
    },

    categoriesExist() {
      return this.propHasCategories !== null ? this.propHasCategories : this.categories.length > 0;
    },

    isDarkTheme() {
      const theme = useTheme();
      return theme.global.current.value.dark;
    }
  },

  methods: {
    ...mapActions(useCategoryStore, ['fetchCategoryMenu', 'navigateToCategory']),

    handleCategoryClick(categoryInfo) {
      console.log('Category clicked:', categoryInfo);
      this.navigateToCategory(categoryInfo);
    },

    async loadFromStore() {
      const store = useCategoryStore();
      this.storeLoading = true;

      try {
        await store.fetchCategoryMenu();
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
  display: flex;
  flex-direction: column;
  padding: 12px;
  max-width: 360px;
  background-color: white;
}

.menu-item-vertical {
  margin-bottom: 8px;
}

.menu-item-vertical:last-child {
  margin-bottom: 0;
}

.theme-dark {
  background-color: #1E1E1E !important;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2) !important;
}

.theme-dark .category-menu-container {
  background-color: #1E1E1E !important;
}

.theme-dark .category-submenu-card {
  background-color: #1E1E1E !important;
}

.theme-dark .nested-item-title:hover {
  background-color: rgba(80, 80, 80, 0.3);
}

.theme-dark .category-btn {
  background-color: #2A2A2A;
}
</style>
