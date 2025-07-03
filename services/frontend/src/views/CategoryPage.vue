<template>
  <div class="catalog-layout">
    <category-filter-panel
        :has-products="hasProducts"
        :is-filter-drawer-open="categoryStore.isFilterDrawerOpen"
        :active-filters-count="categoryStore.activeFiltersCount"
        @toggle-filter-drawer="categoryStore.toggleFilterDrawer"
    />

    <div class="main-content">
      <div class="container-custom mx-auto my-6">
        <category-breadcrumbs
            :master-category="masterCategory"
            :sub-category="subCategory"
            :article-type="articleType"
            :master-category-slug="masterCategorySlug"
            :sub-category-slug="subCategorySlug"
        />

        <category-header
            :title="currentCategoryTitle"
            :description="currentCategoryDescription"
            :search-query="searchQuery"
            :has-products="hasProducts"
            :items-per-page-options="itemsPerPageOptions"
            @clear-search="clearSearch"
            @update:ordering="handleOrderingChange"
            @update:per-page="handleItemsPerPageChange"
        />

        <category-active-filters
            :has-active-filters="categoryStore.hasActiveFilters"
            :is-loading="isLoading"
            :is-loading-filters="isLoadingFilters"
            :active-filters="activeFilters"
            :available-filters="availableFilters"
            @clear-all-filters="clearAllFilters"
            @clear-gender-filter="activeFilters.gender = null"
            @clear-year-filter="activeFilters.min_year = null; activeFilters.max_year = null"
        />

        <category-grid
            :is-loading="isLoading"
            :error="error"
            :products="products"
            :total-items="totalItems"
            :has-products="hasProducts"
            :category-context="currentCategoryTitle"
            :filters-error="filtersError"
            :is-loading-filters="isLoadingFilters"
            @clear-filters-error="filtersError = null"
        />

        <catalog-footer
            :is-empty="isEmpty"
            :has-items="hasItems"
            :current-page="currentPage"
            :total-pages="totalPages"
            @update:page="handlePageChange"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import {computed, onMounted, onUnmounted, provide, watch} from 'vue';
import {useRoute} from 'vue-router';
import {useCategoryStore} from '@/stores/categoryStore';
import {useCategoryProducts} from '@/composables/catalog/useCategoryProducts';
import {useCategoryMeta} from '@/composables/catalog/useCategoryMeta';

import CategoryBreadcrumbs from '@/components/catalog/CategoryBreadcrumbs.vue';
import CategoryHeader from '@/components/catalog/CategoryHeader.vue';
import CategoryFilterPanel from '@/components/catalog/CategoryFilterPanel.vue';
import CategoryActiveFilters from '@/components/catalog/CategoryActiveFilters.vue';
import CategoryGrid from '@/components/catalog/CategoryGrid.vue';
import CatalogFooter from '@/components/catalog/CatalogFooter.vue';

const route = useRoute();
const categoryStore = useCategoryStore();

const {
  masterCategorySlug,
  subCategorySlug,
  masterCategory,
  subCategory,
  articleType,
  currentCategoryTitle,
  currentCategoryDescription
} = useCategoryMeta(route);

const {
  isLoading,
  error,
  products,
  totalPages,
  totalItems,
  currentPage,
  isLoadingFilters,
  filtersError,
  availableFilters,
  activeFilters,
  searchQuery,
  hasProducts,
  isEmpty,
  hasItems,
  itemsPerPageOptions,
  handlePageChange,
  handleItemsPerPageChange,
  handleOrderingChange,
  clearSearch,
  clearAllFilters,
  initialize,
  cleanup,
  disableFilterWatcher,
  enableFilterWatcher,
} = useCategoryProducts(route);

provide('categoryAvailableFilters', availableFilters);
provide('filtersError', filtersError);
provide('hasActiveFilters', computed(() => categoryStore.hasActiveFilters));
provide('clearAllFilters', clearAllFilters);

watch(
    () => [route.params.masterCategory, route.params.subCategory, route.params.articleType],
    async (newParams, oldParams) => {
      if (newParams.some((param, index) => param !== oldParams?.[index])) {
        disableFilterWatcher();
        categoryStore.resetCategoryFilters();

        if (!categoryStore.hasCategories) {
          await categoryStore.fetchCategoryMenu();
        }

        await initialize();
        enableFilterWatcher();
      }
    },
    {immediate: false}
);

const cleanupComponent = () => {
  if (categoryStore.isFilterDrawerOpen) {
    categoryStore.toggleFilterDrawer(false);
  }
  cleanup();
};

onMounted(async () => {
  if (!categoryStore.hasCategories) {
    await categoryStore.fetchCategoryMenu();
  }
  await initialize();
});

onUnmounted(() => {
  cleanupComponent();
});
</script>

<style scoped>
.catalog-layout {
  display: flex;
  min-height: calc(100vh - 64px);
  position: relative;
}

.main-content {
  flex-grow: 1;
  width: 100%;
  display: flex;
  justify-content: center;
}

.container-custom {
  width: 100%;
  max-width: 1280px;
  padding: 0 16px;
  box-sizing: border-box;
}

@media (min-width: 960px) {
  .container-custom {
    padding: 0 24px;
  }
}

@media (min-width: 1440px) {
  .container-custom {
    max-width: 1400px;
  }
}

@media (min-width: 1920px) {
  .container-custom {
    max-width: 1600px;
  }
}
</style>
