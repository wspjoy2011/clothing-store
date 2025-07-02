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

        <active-filters-summary @clear-all-filters="clearAllFilters"/>

        <catalog-grid :has-products="hasProducts"/>

        <catalog-footer
            :is-empty="isEmpty"
            :has-items="hasItems"
            @update:page="handlePageChange"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import {onMounted, onUnmounted} from 'vue';
import {useRoute} from 'vue-router';

import {useProductPagination} from '@/composables/catalog/useProductPagination';
import {useProductFiltering} from '@/composables/catalog/useProductFiltering';
import {useProductSearch} from '@/composables/catalog/useProductSearch';
import {useProductSorting} from '@/composables/catalog/useProductSorting';
import {useProductRouting} from '@/composables/catalog/useProductRouting';
import {useProductUI} from '@/composables/catalog/useProductUI';

import CatalogHeader from '@/components/catalog/CatalogHeader.vue';
import CatalogFilterPanel from '@/components/catalog/CatalogFilterPanel.vue';
import ActiveFiltersSummary from '@/components/catalog/ActiveFiltersSummary.vue';
import CatalogGrid from '@/components/catalog/CatalogGrid.vue';
import CatalogFooter from '@/components/catalog/CatalogFooter.vue';

const route = useRoute();

const {createQueryFromFilters, clearAllFilters} = useProductFiltering(route);
const {hasProducts, isEmpty} = useProductUI();
const {
  itemsPerPageOptions,
  hasItems,
  ensureValidPage,
  handlePageChange,
  handleItemsPerPageChange
} = useProductPagination(createQueryFromFilters, route);
const {clearSearch} = useProductSearch(createQueryFromFilters, route);
const {handleOrderingChange} = useProductSorting(createQueryFromFilters);
const {initialize, cleanup} = useProductRouting(createQueryFromFilters, ensureValidPage);

onMounted(initialize);
onUnmounted(cleanup);
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
