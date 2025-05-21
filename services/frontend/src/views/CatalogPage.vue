<template>
  <div class="catalog-layout">
    <!-- Filter Drawer -->
    <v-navigation-drawer
        v-model="catalogStore.isFilterDrawerOpen"
        location="left"
        temporary
        width="320"
        class="filter-drawer"
    >
      <div class="drawer-header">
        <h3 class="text-h6">Filters</h3>
        <v-btn icon="mdi-close" variant="text" size="small" @click="catalogStore.toggleFilterDrawer(false)"/>
      </div>
      <filter-sidebar/>
    </v-navigation-drawer>

    <!-- Filter Toggle Button -->
    <div v-if="hasProducts" class="filter-toggle-container">
      <v-btn
          icon="mdi-filter"
          variant="outlined"
          size="small"
          class="filter-btn"
          @click="catalogStore.toggleFilterDrawer(true)"
      >
        <v-badge
            :content="catalogStore.activeFiltersCount"
            :value="catalogStore.activeFiltersCount > 0"
            :color="catalogStore.activeFiltersCount > 0 ? 'error' : 'primary'"
            location="top end"
        />
      </v-btn>
    </div>

    <!-- Main Content Area -->
    <div class="main-content">
      <div class="container-custom mx-auto my-6">
        <!-- Page header -->
        <v-row justify="center">
          <v-col cols="12">
            <h1 class="text-h4 font-weight-bold mb-2 text-center">Fashion & Accessories Catalog</h1>

            <!-- Search results indicator -->
            <div v-if="catalogStore.searchQuery" class="text-center mb-6">
              <v-chip
                  color="primary"
                  variant="outlined"
                  size="large"
                  closable
                  @click:close="clearSearch"
                  prepend-icon="mdi-magnify"
              >
                Search results for: "{{ catalogStore.searchQuery }}"
              </v-chip>
            </div>
          </v-col>
        </v-row>

        <!-- Control panel -->
        <v-row v-if="hasProducts" justify="center" align="center" class="mb-3">
          <v-col cols="12" sm="6" md="4" lg="3">
            <product-sorting @update:ordering="handleOrderingChange"/>
          </v-col>

          <v-spacer class="d-none d-md-flex"></v-spacer>

          <v-col cols="12" sm="6" md="4" lg="3" class="d-flex justify-end">
            <items-per-page-select
                :options="itemsPerPageOptions"
                @update:perPage="handleItemsPerPageChange"
            />
          </v-col>
        </v-row>

        <!-- Active filters summary -->
        <v-row v-if="catalogStore.hasActiveFilters && !catalogStore.loading" class="mb-4">
          <v-col cols="12">
            <v-sheet rounded class="pa-3" color="grey-lighten-4">
              <div class="d-flex align-center justify-space-between">
                <div class="d-flex align-center">
                  <v-icon icon="mdi-filter-variant" class="mr-2"/>
                  <span class="text-body-1">Active Filters</span>
                </div>
                <v-btn
                    variant="text"
                    color="primary"
                    density="comfortable"
                    @click="clearAllFilters"
                >
                  Clear All
                </v-btn>
              </div>
            </v-sheet>
          </v-col>
        </v-row>

        <!-- Loader -->
        <content-loader v-if="catalogStore.loading"/>

        <!-- Error message -->
        <error-alert v-if="catalogStore.error" :message="catalogStore.error.message"/>

        <!-- Products grid -->
        <v-row v-if="!catalogStore.loading && !catalogStore.error && catalogStore.products.length > 0">
          <v-col
              v-for="product in catalogStore.products"
              :key="product.product_id"
              cols="12"
              sm="6"
              md="4"
              lg="3"
          >
            <clothes-card :product="product"/>
          </v-col>
        </v-row>

        <!-- Products count indicator -->
        <v-row v-if="hasProducts" justify="center" class="mt-4 mb-4">
          <v-col cols="12" class="text-center">
            <v-chip
                color="primary"
                variant="flat"
                class="px-4 py-2"
                size="large"
            >
              <v-icon start icon="mdi-tag-multiple" class="mr-1"/>
              {{ catalogStore.totalItems }} products found
            </v-chip>
          </v-col>
        </v-row>

        <!-- No products found -->
        <no-items-found
            v-if="isEmpty"
            title="No products found"
            message="Try adjusting your filters or search query"
            icon="mdi-search-off"
        />

        <!-- Pagination  -->
        <v-row justify="center" v-if="hasItems">
          <v-col cols="12" class="px-0">
            <app-pagination
                :current-page="catalogStore.currentPage"
                :total-pages="catalogStore.totalPages"
                @update:page="handlePageChange"
            />
          </v-col>
        </v-row>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue';
import { useRoute } from 'vue-router';

import { useCatalogStore } from '@/stores/catalog';
import { useProductPagination } from '@/composables/catalog/useProductPagination';
import { useProductFiltering } from '@/composables/catalog/useProductFiltering';
import { useProductSearch } from '@/composables/catalog/useProductSearch';
import { useProductSorting } from '@/composables/catalog/useProductSorting';
import { useProductRouting } from '@/composables/catalog/useProductRouting';
import { useProductUI } from '@/composables/catalog/useProductUI';

import ClothesCard from '@/components/catalog/ClothesCard.vue';
import ContentLoader from '@/components/ui/loaders/ContentLoader.vue';
import ErrorAlert from '@/components/ui/alerts/ErrorAlert.vue';
import AppPagination from '@/components/ui/pagination/AppPagination.vue';
import ItemsPerPageSelect from '@/components/ui/pagination/ItemsPerPageSelect.vue';
import NoItemsFound from '@/components/ui/empty-states/NoItemsFound.vue';
import ProductSorting from '@/components/ui/sorting/ProductSorting.vue';
import FilterSidebar from '@/components/ui/filters/FilterSidebar.vue';

const route = useRoute();
const catalogStore = useCatalogStore();

const { createQueryFromFilters, clearAllFilters } = useProductFiltering(route);

const { hasProducts, isEmpty } = useProductUI();

const {
  itemsPerPageOptions,
  hasItems,
  ensureValidPage,
  handlePageChange,
  handleItemsPerPageChange
} = useProductPagination(createQueryFromFilters, route);

const { clearSearch } = useProductSearch(createQueryFromFilters, route);

const { handleOrderingChange } = useProductSorting(createQueryFromFilters);

const { initialize, cleanup } = useProductRouting(createQueryFromFilters, ensureValidPage);

onMounted(initialize);
onUnmounted(cleanup);
</script>

<style scoped>
.catalog-layout {
  display: flex;
  min-height: calc(100vh - 64px);
  position: relative;
}

.filter-drawer {
  box-shadow: 0 0 15px rgba(0, 0, 0, 0.1);
}

.drawer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.filter-toggle-container {
  position: fixed;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  z-index: 5;
}

.filter-btn {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  background-color: white;
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

@media (max-width: 600px) {
  .filter-toggle-container {
    top: auto;
    bottom: 24px;
    left: 24px;
    transform: none;
  }
}
</style>
