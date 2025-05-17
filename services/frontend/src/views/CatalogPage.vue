<template>
  <div class="catalog-layout">
    <!-- Filter Drawer -->
    <v-navigation-drawer
        v-model="isFilterDrawerOpen"
        location="left"
        temporary
        width="320"
        class="filter-drawer"
    >
      <div class="drawer-header">
        <h3 class="text-h6">Filters</h3>
        <v-btn icon="mdi-close" variant="text" size="small" @click="isFilterDrawerOpen = false"/>
      </div>
      <filter-sidebar/>
    </v-navigation-drawer>

    <!-- Filter Toggle Button -->
    <div class="filter-toggle-container">
      <v-btn icon="mdi-filter" variant="outlined" size="small" class="filter-btn" @click="isFilterDrawerOpen = true">
        <v-badge
            :content="activeFiltersCount"
            :value="activeFiltersCount > 0"
            color="primary"
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
        <v-row justify="center" align="center" class="mb-3">
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

        <!-- No products found -->
        <no-items-found
            v-if="!catalogStore.loading && !catalogStore.error && catalogStore.products.length === 0"
            title="No products found"
            message="Sorry, there are no products in this category."
        />

        <!-- Pagination  -->
        <v-row justify="center" v-if="!catalogStore.loading && !catalogStore.error && catalogStore.totalPages > 0">
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
import {onMounted, onUnmounted, watch, ref, computed} from 'vue';
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

const isFilterDrawerOpen = ref(false);

const activeFiltersCount = computed(() => {
  return 0;
});

const props = defineProps({
  page: {
    type: Number,
    default: 1
  },
  perPage: {
    type: Number,
    default: 12
  }
});

const itemsPerPageOptions = [8, 12, 16, 20];

const handleOrderingChange = (ordering) => {
  router.push({
    name: 'catalog',
    query: {
      ...route.query,
      page: 1,
      ordering
    }
  });

  catalogStore.fetchProducts(1, ordering);
};

const handleItemsPerPageChange = (count) => {
  router.push({
    name: 'catalog',
    query: {
      ...route.query,
      page: 1,
      per_page: count
    }
  });

  catalogStore.fetchProducts(1);
};

const handlePageChange = (page) => {
  router.push({
    name: 'catalog',
    query: {
      ...route.query,
      page: page > 1 ? page : undefined
    }
  });

  catalogStore.fetchProducts(page);
};

watch(() => route.query, (newQuery) => {
  const page = parseInt(newQuery.page) || 1;
  const ordering = newQuery.ordering || '-id';

  if (page !== catalogStore.currentPage || ordering !== catalogStore.currentOrdering) {
    catalogStore.fetchProducts(page, ordering);
  }
}, {deep: true});

watch(() => preferencesStore.itemsPerPage, (_newPerPage) => {
  if (catalogStore.totalItems > 0) {
    catalogStore.fetchProducts(catalogStore.currentPage);
  }
});

onMounted(() => {
  const ordering = route.query.ordering || '-id';
  catalogStore.fetchProducts(props.page, ordering);
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
