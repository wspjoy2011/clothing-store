<template>
  <div class="product-info">
    <!-- Product Title -->
    <h1 class="text-h4 font-weight-bold mb-4">
      {{ product.product_display_name }}
    </h1>

    <!-- Product Meta -->
    <v-sheet rounded class="pa-4 mb-4 product-meta-sheet" color="grey-lighten-5">
      <div class="product-meta">
        <div class="meta-item">
          <v-icon icon="mdi-account" class="mr-2" color="primary"/>
          <span class="meta-label">Gender:</span>
          <v-chip
              color="primary"
              variant="outlined"
              size="small"
              class="ml-2"
          >
            {{ product.gender }}
          </v-chip>
        </div>

        <div class="meta-item mt-3">
          <v-icon icon="mdi-calendar" class="mr-2" color="primary"/>
          <span class="meta-label">Year:</span>
          <v-chip
              color="secondary"
              variant="outlined"
              size="small"
              class="ml-2"
          >
            {{ product.year }}
          </v-chip>
        </div>

        <div class="meta-item mt-3">
          <v-icon icon="mdi-identifier" class="mr-2" color="primary"/>
          <span class="meta-label">Product ID:</span>
          <span class="ml-2 font-weight-medium product-id-text">
            #{{ product.product_id }}
          </span>
        </div>
      </div>
    </v-sheet>

    <!-- Action Buttons -->
    <product-action-buttons @go-back="$emit('go-back')"/>
  </div>
</template>

<script setup>
import ProductActionButtons from './ProductActionButtons.vue';

const props = defineProps({
  product: {
    type: Object,
    required: true
  }
});

const emit = defineEmits(['go-back']);
</script>

<style scoped>
.product-info {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.product-meta {
  display: flex;
  flex-direction: column;
}

.meta-item {
  display: flex;
  align-items: center;
}

.meta-label {
  font-weight: 500;
  color: #424242;
}

.product-id-text {
  color: #424242;
}

.v-theme--dark .product-meta-sheet {
  background-color: #2c2c2c !important;
}

.v-theme--dark .meta-label {
  color: #ffffff !important;
}

.v-theme--dark .product-id-text {
  color: #ffffff !important;
}

@media (min-width: 960px) {
  .product-info {
    padding-left: 24px;
  }
}
</style>
