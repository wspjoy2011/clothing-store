<template>
  <div class="catalog-layout">
    <catalog-filter-panel :has-products="hasProducts"/>

    <div class="main-content">
      <div class="container-custom mx-auto my-6">
        <catalog-header
            :has-products="hasProducts"
            :items-per-page-options="itemsPerPageOptions"
            @clear-search="clearSearch"
            @update:ordering="handleOrderingChange"
            @update:per-page="handleItemsPerPageChange"
        />

        <active-filters
            :filter-store="catalogStore"
        />

        <product-grid
            :store="catalogStore"
            :has-products="hasProducts"
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
import {computed, onMounted, onUnmounted, provide} from 'vue';
import {useRoute} from 'vue-router';
import {useCatalogStore} from '@/stores/catalog';

import {useProductPagination} from '@/composables/catalog/useProductPagination';
import {useFiltering} from '@/composables/catalog/useFiltering';
import {useProductSearch} from '@/composables/catalog/useProductSearch';
import {useProductSorting} from '@/composables/catalog/useProductSorting';
import {useProductRouting} from '@/composables/catalog/useProductRouting';
import {useProductUI} from '@/composables/catalog/useProductUI';

import CatalogHeader from '@/components/catalog/CatalogHeader.vue';
import CatalogFilterPanel from '@/components/catalog/FilterPanel.vue';
import ActiveFilters from '@/components/catalog/ActiveFilters.vue';
import ProductGrid from '@/components/catalog/ProductGrid.vue';
import CatalogFooter from '@/components/catalog/Footer.vue';

const route = useRoute();
const catalogStore = useCatalogStore();

const {createQueryFromFilters, clearAllFilters} = useFiltering(route, catalogStore, {
  routeName: 'catalog'
});

provide('clearAllFilters', clearAllFilters);
provide('filterStore', computed(() => catalogStore));

const {hasProducts, isEmpty} = useProductUI();

const {
  itemsPerPageOptions,
  hasItems,
  ensureValidPage,
  handleItemsPerPageChange
} = useProductPagination(catalogStore, createQueryFromFilters, route, {
  routeName: 'catalog',
  fetchMethod: 'fetchProducts'
});

const {clearSearch} = useProductSearch(createQueryFromFilters, route);
const {handleOrderingChange} = useProductSorting(createQueryFromFilters);
const {initialize, cleanup} = useProductRouting(createQueryFromFilters, ensureValidPage);

onMounted(() => {
  initialize();
});

onUnmounted(() => {
  cleanup();
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
