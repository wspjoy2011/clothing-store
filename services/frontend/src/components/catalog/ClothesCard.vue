<template>
  <v-card
      :class="['mx-auto my-3 product-card', { 'out-of-stock': !isAvailable }]"
      :elevation="hover ? 8 : 2"
      @mouseenter="hover = true"
      @mouseleave="hover = false"
  >
    <div class="position-relative">
      <div v-if="imageLoading" class="image-loader">
        <v-progress-circular color="primary" indeterminate size="30"/>
      </div>
      <v-img
          :src="props.product.image_url"
          height="250"
          cover
          class="product-image"
          @load="imageLoaded"
          @error="imageLoaded"
      />

      <!-- Out of Stock Overlay -->
      <div v-if="!isAvailable" class="out-of-stock-overlay">
        <v-chip
            color="error"
            variant="elevated"
            size="large"
            class="font-weight-bold"
        >
          Out of Stock
        </v-chip>
      </div>
    </div>

    <v-card-title class="text-subtitle-1 font-weight-bold d-block text-truncate">
      {{ props.product.product_display_name }}
    </v-card-title>

    <v-card-subtitle>
      <span class="font-weight-medium">{{ props.product.gender }}</span>
      <span class="ms-2 text-medium-emphasis text-caption">{{ props.product.year }}</span>
    </v-card-subtitle>

    <!-- Price Section -->
    <v-card-text v-if="product.inventory" class="py-2">
      <div class="price-section">
        <div v-if="hasDiscount" class="price-container price-inline">
          <span class="original-price">
            {{ product.inventory.base_price }} {{ product.inventory.currency }}
          </span>
          <span class="sale-price">
            {{ product.inventory.sale_price }} {{ product.inventory.currency }}
          </span>
        </div>

        <!-- Regular Price Display -->
        <div v-else class="price-container">
          <span class="base-price">
            {{ product.inventory.base_price }} {{ product.inventory.currency }}
          </span>
        </div>
      </div>
    </v-card-text>

    <v-card-actions>
      <v-btn
          :disabled="!isAvailable"
          :color="isAvailable ? 'primary' : 'grey'"
          variant="flat"
          class="text-none"
          block
          @click="goToProductDetail"
      >
        {{ isAvailable ? 'View Details' : 'Unavailable' }}
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script setup>
import {ref, computed} from 'vue';
import {useRouter} from 'vue-router';

const props = defineProps({
  product: {
    type: Object,
    required: true,
    validator: (product) => {
      return [
        'product_id',
        'gender',
        'year',
        'product_display_name',
        'image_url',
        'slug'
      ].every(prop => prop in product);
    }
  }
});

const router = useRouter();
const hover = ref(false);
const imageLoading = ref(true);

const isAvailable = computed(() =>
    props.product.inventory?.is_in_stock && props.product.inventory?.is_active
);

const hasDiscount = computed(() => {
  if (!props.product.inventory?.sale_price || !props.product.inventory?.base_price) {
    return false;
  }
  return parseFloat(props.product.inventory.sale_price) < parseFloat(props.product.inventory.base_price);
});

const imageLoaded = () => {
  imageLoading.value = false;
};

const goToProductDetail = () => {
  if (!isAvailable.value) return;

  router.push({
    name: 'product-detail',
    params: {
      productSlug: props.product.slug
    }
  });
};
</script>

<style scoped>
.product-card {
  transition: transform 0.2s ease-in-out;
  width: 100%;
  cursor: pointer;
}

.product-card:hover {
  transform: translateY(-5px);
}

.product-image {
  transition: opacity 0.3s;
}

.product-image:hover {
  opacity: 0.85;
}

.position-relative {
  position: relative;
  height: 250px;
}

.image-loader {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: rgba(245, 245, 245, 0.7);
  z-index: 1;
}

.out-of-stock {
  filter: grayscale(100%);
  opacity: 0.6;
}

.out-of-stock-overlay {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 2;
}

.out-of-stock .product-card:hover {
  transform: none;
}

.price-section {
  display: flex;
  flex-direction: column;
  gap: 4px;
  align-items: flex-start;
}

.price-container {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.price-inline {
  flex-direction: row !important;
  align-items: center;
  gap: 8px !important;
}

.original-price {
  text-decoration: line-through;
  color: #666;
  font-size: 0.9rem;
  line-height: 1.2;
}

.sale-price {
  color: #d32f2f;
  font-weight: bold;
  font-size: 1.1rem;
  line-height: 1.2;
}

.base-price {
  font-weight: bold;
  color: #1976d2;
  font-size: 1.1rem;
  line-height: 1.2;
}

.out-of-stock:hover {
  transform: none;
}

.out-of-stock .product-image:hover {
  opacity: 1;
}
</style>
