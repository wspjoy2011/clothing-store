<template>
  <!-- Main container with custom styling for proper spacing and alignment -->
  <div class="container-custom mx-auto my-6">
    <!-- Page header section -->
    <v-row justify="center">
      <v-col cols="12">
        <h1 class="text-h4 font-weight-bold mb-6 text-center">Fashion & Accessories Catalog</h1>
      </v-col>
    </v-row>

    <!-- Control panel section with sorting and items per page controls -->
    <v-row justify="center">
      <v-col cols="12" class="d-flex justify-space-between align-center">
        <product-sorting
            @update:ordering="handleOrderingChange"
        />
        <items-per-page-select
            :options="itemsPerPageOptions"
            @update:perPage="handleItemsPerPageChange"
        />
      </v-col>
    </v-row>

    <!-- Loader - displayed while products are being fetched -->
    <content-loader v-if="catalogStore.loading"/>

    <!-- Error message - displayed when an error occurs during data fetching -->
    <error-alert v-if="catalogStore.error" :message="catalogStore.error.message"/>

    <!-- Products grid - displayed when products are successfully loaded -->
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

    <!-- No products found message - displayed when the product list is empty -->
    <no-items-found
        v-if="!catalogStore.loading && !catalogStore.error && catalogStore.products.length === 0"
        title="No products found"
        message="Sorry, there are no products in this category."
    />

    <!-- Pagination section - displayed when there are multiple pages of products -->
    <v-row justify="center">
      <v-col cols="12" class="d-flex justify-center">
        <app-pagination
            v-if="!catalogStore.loading && !catalogStore.error && catalogStore.totalPages > 0"
            :current-page="catalogStore.currentPage"
            :total-pages="catalogStore.totalPages"
            @update:page="handlePageChange"
        />
      </v-col>
    </v-row>
  </div>
</template>

<script setup>
import {onMounted, onUnmounted, watch} from 'vue';
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

const router = useRouter();
const route = useRoute();
const preferencesStore = useUserPreferencesStore();
const catalogStore = useCatalogStore();

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
.container-custom {
  width: 100%;
  max-width: 1280px;
  padding-left: 16px;
  padding-right: 16px;
  box-sizing: border-box;
}

@media (min-width: 960px) {
  .container-custom {
    padding-left: 24px;
    padding-right: 24px;
  }
}
</style>
