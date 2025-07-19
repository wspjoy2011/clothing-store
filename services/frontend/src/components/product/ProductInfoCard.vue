<template>
  <div class="product-info">
    <!-- Product Title -->
    <h1 class="text-h4 font-weight-bold mb-4">
      {{ product.product_display_name }}
    </h1>

    <!-- Price Section -->
    <div v-if="product.inventory" class="mb-4">
      <div class="price-section">
        <!-- Discount Price Display -->
        <div v-if="hasDiscount" class="price-container price-inline">
          <span class="original-price text-h5">
            {{ product.inventory.base_price }} {{ product.inventory.currency }}
          </span>
          <span class="sale-price text-h4">
            {{ product.inventory.sale_price }} {{ product.inventory.currency }}
          </span>
        </div>

        <!-- Regular Price Display -->
        <div v-else class="price-container">
          <span class="base-price text-h4">
            {{ product.inventory.base_price }} {{ product.inventory.currency }}
          </span>
        </div>
      </div>
    </div>

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

        <!-- Available Quantity -->
        <div v-if="product.inventory" class="meta-item mt-3">
          <v-icon icon="mdi-package-variant" class="mr-2" color="primary"/>
          <span class="meta-label">Available:</span>
          <v-chip
              :color="stockChipColor"
              variant="outlined"
              size="small"
              class="ml-2"
          >
            {{ stockText }}
          </v-chip>
        </div>
      </div>
    </v-sheet>

    <!-- Action Buttons -->
    <product-action-buttons
        :product="product"
        @go-back="$emit('go-back')"
    />
  </div>
</template>

<script setup>
import {computed} from 'vue';
import ProductActionButtons from './ProductActionButtons.vue';

const props = defineProps({
  product: {
    type: Object,
    required: true
  }
});

const emit = defineEmits(['go-back']);

const hasDiscount = computed(() => {
  if (!props.product.inventory?.sale_price || !props.product.inventory?.base_price) {
    return false;
  }
  return parseFloat(props.product.inventory.sale_price) < parseFloat(props.product.inventory.base_price);
});

const stockText = computed(() => {
  if (!props.product.inventory) return 'N/A';

  const availableQty = props.product.inventory.available_quantity;

  if (!props.product.inventory.is_active || !props.product.inventory.is_in_stock) {
    return 'Out of Stock';
  }

  if (availableQty <= 0) {
    return 'Out of Stock';
  } else if (availableQty <= 5) {
    return `${availableQty} left`;
  } else {
    return 'In Stock';
  }
});

const stockChipColor = computed(() => {
  if (!props.product.inventory) return 'grey';

  const availableQty = props.product.inventory.available_quantity;

  if (!props.product.inventory.is_active || !props.product.inventory.is_in_stock || availableQty <= 0) {
    return 'error';
  } else if (availableQty <= 5) {
    return 'warning';
  } else {
    return 'success';
  }
});
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

.price-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
  align-items: flex-start;
  margin-bottom: 16px;
}

.price-container {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.price-inline {
  flex-direction: row !important;
  align-items: center;
  gap: 16px !important;
}

.original-price {
  text-decoration: line-through;
  color: #666;
  line-height: 1.2;
}

.sale-price {
  color: #d32f2f;
  font-weight: bold;
  line-height: 1.2;
}

.base-price {
  font-weight: bold;
  color: #1976d2;
  line-height: 1.2;
}

@media (min-width: 960px) {
  .product-info {
    padding-left: 24px;
  }
}
</style>
