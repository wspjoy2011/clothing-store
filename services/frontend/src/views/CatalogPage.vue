<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <h1 class="text-h4 font-weight-bold mb-6 text-center">Fashion & Accessories Catalog</h1>
      </v-col>
    </v-row>

    <!-- Per page -->
    <v-row>
      <v-col cols="12" class="d-flex justify-end">
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

    <!-- Pagination -->
    <app-pagination
        v-if="!catalogStore.loading && !catalogStore.error && catalogStore.totalPages > 0"
        :current-page="catalogStore.currentPage"
        :total-pages="catalogStore.totalPages"
        @update:page="handlePageChange"
    />

    <!-- No products found -->
    <no-items-found
        v-if="!catalogStore.loading && !catalogStore.error && catalogStore.products.length === 0"
        title="No products found"
        message="Sorry, there are no products in this category."
    />
  </v-container>
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

  if (page !== catalogStore.currentPage) {
    catalogStore.fetchProducts(page);
  }
}, { deep: true });

watch(() => preferencesStore.itemsPerPage, (_newPerPage) => {
  if (catalogStore.totalItems > 0) {
    catalogStore.fetchProducts(catalogStore.currentPage);
  }
});

onMounted(() => {
  catalogStore.fetchProducts(props.page);
});

onUnmounted(() => {
  catalogStore.resetState();
});
</script>
