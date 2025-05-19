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
            <h1 class="text-h4 font-weight-bold mb-6 text-center">Fashion & Accessories Catalog</h1>
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
            message="Sorry, there are no products in this category."
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
import {onMounted, onUnmounted, watch, provide, computed} from 'vue';
import {useRouter, useRoute} from 'vue-router';

import {useUserPreferencesStore} from '@/stores/userPreferences';
import {useCatalogStore} from '@/stores/catalog';
import ClothesCard from '@/components/catalog/ClothesCard.vue';
import ContentLoader from '@/components/ui/loaders/ContentLoader.vue';
import ErrorAlert from '@/components/ui/alerts/ErrorAlert.vue';
import AppPagination from '@/components/ui/pagination/AppPagination.vue';
import ItemsPerPageSelect from '@/components/ui/pagination/ItemsPerPageSelect.vue';
import NoItemsFound from '@/components/ui/empty-states/NoItemsFound.vue';
import ProductSorting from '@/components/ui/sorting/ProductSorting.vue';
import FilterSidebar from '@/components/ui/filters/FilterSidebar.vue';

const router = useRouter();
const route = useRoute();
const preferencesStore = useUserPreferencesStore();
const catalogStore = useCatalogStore();

const hasProducts = computed(() =>
    !catalogStore.loading &&
    !catalogStore.error &&
    catalogStore.products.length > 0
);

const isEmpty = computed(() =>
    !catalogStore.loading &&
    !catalogStore.error &&
    catalogStore.products.length === 0
);

const hasItems = computed(() =>
  !catalogStore.loading &&
  !catalogStore.error &&
  catalogStore.totalPages > 0
);

const itemsPerPageOptions = [8, 12, 16, 20];

const ensureValidPage = (page) => {
  if (catalogStore.totalPages > 0 && page > catalogStore.totalPages) {
    return catalogStore.totalPages;
  }
  return page;
};

const createQueryFromFilters = () => {
  const query = {...route.query};
  const activeFilters = catalogStore.activeFilters;
  const availableFilters = catalogStore.availableFilters;

  if (activeFilters.gender !== null) {
    query.gender = activeFilters.gender;
  } else {
    delete query.gender;
  }

  if (
      availableFilters?.year &&
      activeFilters.min_year !== null &&
      activeFilters.min_year !== availableFilters.year.min
  ) {
    query.min_year = activeFilters.min_year;
  } else {
    delete query.min_year;
  }

  if (
      availableFilters?.year &&
      activeFilters.max_year !== null &&
      activeFilters.max_year !== availableFilters.year.max
  ) {
    query.max_year = activeFilters.max_year;
  } else {
    delete query.max_year;
  }

  return query;
};

const clearAllFilters = () => {
  const drawerWasOpen = catalogStore.isFilterDrawerOpen;

  catalogStore.clearFilters();

  const newQuery = {};
  if (route.query.ordering && route.query.ordering !== '-id') {
    newQuery.ordering = route.query.ordering;
  }
  if (route.query.per_page) {
    newQuery.per_page = route.query.per_page;
  }

  router.push({
    name: 'catalog',
    query: newQuery
  }).then(() => {
    catalogStore.fetchProducts(1);

    if (drawerWasOpen) {
      catalogStore.toggleFilterDrawer(true);
    }
  });
};

provide('clearAllFilters', clearAllFilters);

const handleOrderingChange = (ordering) => {
  const query = createQueryFromFilters();

  router.push({
    name: 'catalog',
    query: {
      ...query,
      page: undefined,
      ordering: ordering !== '-id' ? ordering : undefined
    }
  });

  catalogStore.setOrdering(ordering);
  catalogStore.fetchProducts(1, ordering);
};

const handleItemsPerPageChange = (count) => {
  const query = createQueryFromFilters();

  preferencesStore.setItemsPerPage(count);

  catalogStore.fetchProducts(1).then(() => {
    if (catalogStore.currentPage > catalogStore.totalPages) {
      const correctedPage = catalogStore.totalPages > 0 ? catalogStore.totalPages : 1;

      router.push({
        name: 'catalog',
        query: {
          ...query,
          page: correctedPage > 1 ? correctedPage : undefined,
          per_page: count
        }
      });

      if (correctedPage !== 1) {
        catalogStore.fetchProducts(correctedPage);
      }
    } else {
      router.push({
        name: 'catalog',
        query: {
          ...query,
          page: undefined,
          per_page: count
        }
      });
    }
  });
};

const handlePageChange = (page) => {
  const validPage = ensureValidPage(page);
  const query = createQueryFromFilters();

  router.push({
    name: 'catalog',
    query: {
      ...query,
      page: validPage > 1 ? validPage : undefined
    }
  });

  catalogStore.fetchProducts(validPage);
};

watch(() => catalogStore.activeFilters, () => {
  if (catalogStore.isUpdatingFilters) return;

  const drawerWasOpen = catalogStore.isFilterDrawerOpen;

  router.push({
    name: 'catalog',
    query: {
      ...createQueryFromFilters(),
      page: undefined,
      ordering: catalogStore.currentOrdering !== '-id' ? catalogStore.currentOrdering : undefined,
      per_page: route.query.per_page
    }
  }).then(() => {
    catalogStore.fetchProducts(1);

    if (drawerWasOpen) {
      catalogStore.toggleFilterDrawer(true);
    }
  });
}, {deep: true});

watch(() => route.query, (newQuery, oldQuery) => {
  const filterParamsChanged =
      newQuery.gender !== oldQuery.gender ||
      newQuery.min_year !== oldQuery.min_year ||
      newQuery.max_year !== oldQuery.max_year;

  if (filterParamsChanged) {
    catalogStore.loadFiltersFromQuery(newQuery);
  }

  const pageChanged = newQuery.page !== oldQuery.page;
  const orderingChanged = newQuery.ordering !== oldQuery.ordering;
  const perPageChanged = newQuery.per_page !== oldQuery.per_page;

  if (filterParamsChanged || pageChanged || orderingChanged || perPageChanged) {
    const page = parseInt(newQuery.page) || 1;
    const ordering = newQuery.ordering || '-id';

    catalogStore.fetchProducts(page, ordering).then(() => {
      const validPage = ensureValidPage(page);
      if (validPage !== page) {
        router.push({
          name: 'catalog',
          query: {
            ...createQueryFromFilters(),
            page: validPage > 1 ? validPage : undefined,
            ordering: catalogStore.currentOrdering !== '-id' ? catalogStore.currentOrdering : undefined,
            per_page: newQuery.per_page
          }
        });

        catalogStore.fetchProducts(validPage, ordering);
      }
    });
  }
}, {deep: true});

watch(() => preferencesStore.itemsPerPage, () => {
  if (catalogStore.totalItems > 0) {
    const validPage = ensureValidPage(catalogStore.currentPage);
    if (validPage !== catalogStore.currentPage) {
      catalogStore.fetchProducts(validPage);
    } else {
      catalogStore.fetchProducts(catalogStore.currentPage);
    }
  }
});

onMounted(() => {
  const page = parseInt(route.query.page) || 1;
  const ordering = route.query.ordering || '-id';

  catalogStore.fetchFilters().then(() => {
    catalogStore.loadFiltersFromQuery(route.query);

    catalogStore.fetchProducts(page, ordering).then(() => {
      const validPage = ensureValidPage(page);
      if (validPage !== page) {
        router.push({
          name: 'catalog',
          query: {
            ...createQueryFromFilters(),
            page: validPage > 1 ? validPage : undefined,
            ordering: ordering !== '-id' ? ordering : undefined,
            per_page: route.query.per_page
          }
        });

        catalogStore.fetchProducts(validPage, ordering);
      }
    });
  });
});

onUnmounted(() => {
  catalogStore.resetState();
});
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
