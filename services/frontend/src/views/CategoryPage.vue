<template>
  <div class="catalog-layout">
    <catalog-filter-panel :has-products="hasProducts"/>

    <div class="main-content">
      <div class="container-custom mx-auto my-6">
        <category-breadcrumbs
            :master-category="masterCategory"
            :sub-category="subCategory"
            :article-type="articleType"
            :master-category-slug="masterCategorySlug"
            :sub-category-slug="subCategorySlug"
        />

        <header-component
            :store="categoryStore"
            :title="currentCategoryTitle"
            :description="currentCategoryDescription"
            :show-divider="true"
            :has-products="hasProducts"
            :items-per-page-options="itemsPerPageOptions"
            @clear-search="clearSearchHandler"
            @update:ordering="handleOrderingChangeHandler"
            @update:per-page="handleItemsPerPageChangeHandler"
        />

        <active-filters
            :filter-store="categoryStore"
        />

        <product-grid
            :store="categoryStore"
            :has-products="hasProducts"
            :context="currentCategoryTitle"
            :filters-error="filtersError"
            :is-loading-filters="isLoadingFilters"
            @clear-filters-error="filtersError = null"
        />

        <catalog-footer
            :is-empty="isEmpty"
            :has-items="hasItems"
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
import {useFiltering} from '@/composables/catalog/useFiltering';

import CategoryBreadcrumbs from '@/components/catalog/CategoryBreadcrumbs.vue';
import HeaderComponent from '@/components/catalog/Header.vue';
import CatalogFilterPanel from '@/components/catalog/FilterPanel.vue';
import ActiveFilters from '@/components/catalog/ActiveFilters.vue';
import ProductGrid from '@/components/catalog/ProductGrid.vue';
import CatalogFooter from '@/components/catalog/Footer.vue';

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
  totalPages,
  totalItems,
  currentPage,
  isLoadingFilters,
  filtersError,
  activeFilters,
  hasProducts,
  isEmpty,
  hasItems,
  itemsPerPageOptions,
  handlePageChange,
  handleItemsPerPageChange,
  handleOrderingChange,
  clearSearch,
  initialize,
  cleanup,
  fetchProducts
} = useCategoryProducts(route);

const {createQueryFromFilters, disableFilterWatcher, enableFilterWatcher} = useFiltering(route, categoryStore, {
  routeName: 'category',
  fetchProducts
});

const handlePageChangeHandler = handlePageChange(createQueryFromFilters);
const handleItemsPerPageChangeHandler = handleItemsPerPageChange(createQueryFromFilters);
const handleOrderingChangeHandler = handleOrderingChange(createQueryFromFilters);
const clearSearchHandler = clearSearch(createQueryFromFilters);

const paginationData = computed(() => ({
  currentPage: currentPage.value,
  totalPages: totalPages.value,
  totalItems: totalItems.value,
  hasItems: hasItems.value,
  itemsPerPageOptions
}));

const paginationHandlers = computed(() => ({
  handlePageChange: handlePageChangeHandler,
  handleItemsPerPageChange: handleItemsPerPageChangeHandler
}));

const categoryPaginationHandlers = computed(() => ({
  handlePageChange: handlePageChangeHandler,
  handleItemsPerPageChange: handleItemsPerPageChangeHandler
}));

provide('paginationData', paginationData);
provide('paginationHandlers', paginationHandlers);
provide('categoryPaginationHandlers', categoryPaginationHandlers);
provide('filterStore', computed(() => categoryStore));

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
