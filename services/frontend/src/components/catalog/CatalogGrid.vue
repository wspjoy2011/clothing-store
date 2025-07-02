<template>
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
</template>

<script setup>
import {useCatalogStore} from '@/stores/catalog';
import ClothesCard from '@/components/catalog/ClothesCard.vue';
import ContentLoader from '@/components/ui/loaders/ContentLoader.vue';
import ErrorAlert from '@/components/ui/alerts/ErrorAlert.vue';

const catalogStore = useCatalogStore();

defineProps({
  hasProducts: {
    type: Boolean,
    required: true
  }
});
</script>
