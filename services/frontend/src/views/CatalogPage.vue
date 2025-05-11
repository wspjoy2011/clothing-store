<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <h1 class="text-h4 font-weight-bold mb-6">Clothing Catalog</h1>
      </v-col>
    </v-row>

    <!-- Loader -->
    <div v-if="loading" class="d-flex justify-center align-center my-10">
      <v-progress-circular
          color="primary"
          indeterminate
          size="64"
      ></v-progress-circular>
    </div>

    <!-- Error message -->
    <v-alert
        v-if="error"
        type="error"
        variant="tonal"
        class="mb-6"
    >
      {{ error.message }}
    </v-alert>

    <!-- Products grid -->
    <v-row v-if="!loading && !error">
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
    <v-row v-if="!loading && !error && totalPages > 0">
      <v-col cols="12" class="d-flex justify-center mt-6">
        <v-pagination
            v-model="currentPage"
            :length="totalPages"
            rounded
            @update:model-value="fetchProducts"
        ></v-pagination>
      </v-col>
    </v-row>

    <!-- No products found -->
    <v-row v-if="!loading && !error && products.length === 0">
      <v-col cols="12" class="text-center my-10">
        <v-icon icon="mdi-alert-circle-outline" size="x-large" class="mb-4"></v-icon>
        <h3 class="text-h5">No products found</h3>
        <p class="text-body-1 mt-2">Sorry, there are no products in this category.</p>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import {ref, onMounted} from 'vue';
import ClothesCard from '@/components/catalog/ClothesCard.vue';
import catalogService from '@/services/catalogService';

const products = ref([]);
const loading = ref(true);
const error = ref(null);
const currentPage = ref(1);
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

onMounted(() => {
  fetchProducts();
});
</script>
