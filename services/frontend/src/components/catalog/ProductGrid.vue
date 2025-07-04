<template>
  <!-- Loader -->
  <content-loader v-if="store.loading"/>

  <!-- Error message -->
  <error-alert v-if="store.error" :message="store.error.message"/>

  <!-- Filter loading error -->
  <v-row v-if="filtersError && !isLoadingFilters" class="mb-4">
    <v-col cols="12">
      <v-alert
          type="warning"
          variant="tonal"
          closable
          @click:close="clearFiltersError"
      >
        <template v-slot:title>
          <span class="text-subtitle-1 font-weight-medium">Filter Loading Error</span>
        </template>
        <span class="text-body-2">
          Unable to load filters for this category. Some filtering options may not be available.
        </span>
      </v-alert>
    </v-col>
  </v-row>

  <!-- Products grid -->
  <v-row v-if="!store.loading && !store.error && store.products.length > 0">
    <v-col
        v-for="product in store.products"
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
        {{ store.totalItems }} products found{{ context ? ` in ${context}` : '' }}
      </v-chip>
    </v-col>
  </v-row>
</template>

<script setup>
import ClothesCard from '@/components/catalog/ClothesCard.vue';
import ContentLoader from '@/components/ui/loaders/ContentLoader.vue';
import ErrorAlert from '@/components/ui/alerts/ErrorAlert.vue';

const props = defineProps({
  store: {
    type: Object,
    required: true
  },
  hasProducts: {
    type: Boolean,
    required: true
  },
  context: {
    type: String,
    default: null
  },
  filtersError: {
    type: Object,
    default: null
  },
  isLoadingFilters: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['clear-filters-error']);

const clearFiltersError = () => {
  emit('clear-filters-error');
};
</script>
