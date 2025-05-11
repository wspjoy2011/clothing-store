<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <h1 class="text-h4 font-weight-bold mb-6 text-center">Fashion & Accessories Catalog</h1>
      </v-col>
    </v-row>

    <!-- Loader -->
    <content-loader v-if="loading" />

    <!-- Error message -->
    <error-alert v-if="error" :message="error.message" />

    <!-- Products grid -->
    <v-row v-if="!loading && !error && products.length > 0">
      <v-col
          v-for="product in products"
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
      v-if="!loading && !error && totalPages > 0"
      :current-page="currentPage"
      :total-pages="totalPages"
      @update:page="handlePageChange"
    />

    <!-- No products found -->
    <no-items-found
      v-if="!loading && !error && products.length === 0"
      title="No products found"
      message="Sorry, there are no products in this category."
    />
  </v-container>
</template>

<script setup>
import {ref, onMounted, watch} from 'vue';
import {useRouter, useRoute} from 'vue-router';
import ClothesCard from '@/components/catalog/ClothesCard.vue';
import ContentLoader from '@/components/ui/loaders/ContentLoader.vue';
import ErrorAlert from '@/components/ui/alerts/ErrorAlert.vue';
import AppPagination from '@/components/ui/pagination/AppPagination.vue';
import NoItemsFound from '@/components/ui/empty-states/NoItemsFound.vue';
import catalogService from '@/services/catalogService';

const router = useRouter();
const route = useRoute();

const props = defineProps({
  page: {
    type: Number,
    default: 1
  }
});

const products = ref([]);
const loading = ref(true);
const error = ref(null);
const currentPage = ref(props.page);
const totalPages = ref(0);
const totalItems = ref(0);
const perPage = ref(12);

const fetchProducts = async (page = currentPage.value) => {
  loading.value = true;
  error.value = null;

  try {
    const response = await catalogService.getProducts(page, perPage.value);
    products.value = response.products;
    totalPages.value = response.total_pages;
    totalItems.value = response.total_items;
    currentPage.value = page;
  } catch (err) {
    error.value = err;
    products.value = [];
  } finally {
    loading.value = false;
  }
};

const handlePageChange = (page) => {
  router.push({
    name: 'catalog',
    query: { page: page > 1 ? page : undefined }
  });

  fetchProducts(page);
};

watch(() => route.query.page, (newPage) => {
  const page = parseInt(newPage) || 1;
  if (page !== currentPage.value) {
    fetchProducts(page);
  }
});

onMounted(() => {
  fetchProducts(props.page);
});
</script>
