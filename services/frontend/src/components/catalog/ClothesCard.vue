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

      <!-- Stock Badge - Show only if not in cart -->
      <div v-if="isAvailable && !productInCart" class="stock-badge">
        <v-chip
            color="success"
            variant="elevated"
            size="small"
            class="font-weight-medium"
        >
          {{ availableQuantity }} in stock
        </v-chip>
      </div>

      <!-- In Cart Badge - Show when product is in cart -->
      <div v-if="productInCart" class="cart-badge">
        <v-chip
            color="success"
            variant="elevated"
            size="small"
            class="font-weight-bold"
        >
          <v-icon start size="16">mdi-check-circle</v-icon>
          In Cart
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
            {{ formattedBasePrice }}
          </span>
          <span class="sale-price">
            {{ formattedSalePrice }}
          </span>
        </div>

        <!-- Regular Price Display -->
        <div v-else class="price-container">
          <span class="base-price">
            {{ formattedBasePrice }}
          </span>
        </div>
      </div>
    </v-card-text>

    <v-card-actions class="px-3 pb-3">
      <div class="card-controls">
        <!-- Quantity Controls - Only show if NOT in cart -->
        <div v-if="isAvailable && !productInCart" class="quantity-section">
          <div class="quantity-row">
            <span class="text-caption text-medium-emphasis">Quantity:</span>
            <div class="quantity-controls">
              <v-btn
                  icon
                  size="x-small"
                  variant="outlined"
                  color="primary"
                  :disabled="quantity <= 1"
                  @click="decreaseQuantity"
              >
                <v-icon size="14">mdi-minus</v-icon>
              </v-btn>

              <span class="quantity-display">{{ quantity }}</span>

              <v-btn
                  icon
                  size="x-small"
                  variant="outlined"
                  color="primary"
                  :disabled="quantity >= availableQuantity"
                  @click="increaseQuantity"
              >
                <v-icon size="14">mdi-plus</v-icon>
              </v-btn>
            </div>
          </div>
        </div>

        <!-- In Cart Status - Show when product is in cart -->
        <div v-if="productInCart" class="in-cart-indicator">
          <v-icon color="success" size="24">mdi-check-circle</v-icon>
          <span class="in-cart-text">
            {{ cartDisplayInfo.displayText }}
          </span>
        </div>

        <!-- Action Buttons -->
        <div class="action-buttons">
          <!-- Add to Cart Button - Show only if NOT in cart -->
          <v-btn
              v-if="isAvailable && !productInCart"
              :loading="isAddingItem"
              :disabled="!isAvailable || isAddingItem"
              color="primary"
              variant="flat"
              class="text-none add-to-cart-btn"
              block
              @click="handleAddToCart"
          >
            <v-icon start>mdi-cart-plus</v-icon>
            Add to Cart
          </v-btn>

          <!-- Remove from Cart Button - Show when in cart (placeholder) -->
          <v-btn
              v-if="productInCart"
              color="error"
              variant="flat"
              class="text-none remove-from-cart-btn"
              block
              disabled
              @click="handleRemoveFromCart"
          >
            <v-icon start>mdi-cart-remove</v-icon>
            Remove from Cart
          </v-btn>

          <!-- View Details Button -->
          <v-btn
              :disabled="!isAvailable"
              :color="getActionButtonColor()"
              variant="outlined"
              class="text-none view-details-btn"
              block
              @click="goToProductDetail"
          >
            <v-icon start>mdi-eye</v-icon>
            {{ getActionButtonText('View Details') }}
          </v-btn>
        </div>
      </div>
    </v-card-actions>

    <!-- Error Alert -->
    <v-alert
        v-if="addItemError"
        type="error"
        variant="tonal"
        class="ma-3 mt-0"
        closable
        @click:close="clearAddItemError"
    >
      <template v-slot:title>
        <span class="text-subtitle-2">Failed to add to cart</span>
      </template>
      <span class="text-body-2">{{ addItemError }}</span>
    </v-alert>
  </v-card>
</template>

<script setup>
import {ref, toRef, computed, watch} from 'vue';
import {useRouter} from 'vue-router';
import {useProductInventory} from '@/composables/product/useProductInventory';
import {useCart} from '@/composables/cart/useCart.js';

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
const quantity = ref(1);

const productRef = toRef(props, 'product');
const {
  isAvailable,
  hasDiscount,
  formattedBasePrice,
  formattedSalePrice,
  getActionButtonText,
  getActionButtonColor
} = useProductInventory(productRef);

const {
  isAddingItem,
  addItemError,
  addItemToCart,
  clearAddItemError,
  isProductInCart,
  getCartItemDisplayInfo
} = useCart();

const productInCart = isProductInCart(props.product.product_id);
const cartDisplayInfo = getCartItemDisplayInfo(props.product.product_id);

const availableQuantity = computed(() => {
  return props.product.inventory?.available_quantity || 0;
});

const imageLoaded = () => {
  imageLoading.value = false;
};

const increaseQuantity = () => {
  if (quantity.value < availableQuantity.value) {
    quantity.value++;
  }
};

const decreaseQuantity = () => {
  if (quantity.value > 1) {
    quantity.value--;
  }
};

const handleAddToCart = async () => {
  if (!isAvailable.value || isAddingItem.value || productInCart.value) return;

  try {
    await addItemToCart({
      product_id: props.product.product_id,
      quantity: quantity.value
    });
    quantity.value = 1;
  } catch (error) {
    console.error('Failed to add item to cart:', error);
  }
};

const handleRemoveFromCart = () => {
  console.log('Remove from cart functionality coming soon!');
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

.stock-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  z-index: 2;
}

.cart-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  z-index: 2;
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

.card-controls {
  display: flex;
  flex-direction: column;
  width: 100%;
  gap: 16px;
}

.quantity-section {
  width: 100%;
}

.quantity-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.quantity-controls {
  display: flex;
  align-items: center;
  gap: 12px;
}

.quantity-display {
  min-width: 20px;
  text-align: center;
  font-weight: bold;
  font-size: 0.9rem;
}

.in-cart-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px;
  width: 100%;
}

.in-cart-text {
  font-size: 0.875rem;
  font-weight: 600;
  color: #2e7d32;
}

:deep(.v-theme--dark) .in-cart-text {
  color: #4caf50;
}

.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 8px;
  width: 100%;
}

.remove-from-cart-btn {
  position: relative;
}

@media (min-width: 1450px) {
  .card-controls {
    flex-direction: row;
    align-items: flex-start;
    gap: 16px;
  }

  .quantity-section {
    flex: 0 0 auto;
    min-width: 120px;
    max-width: 120px;
  }

  .in-cart-indicator {
    flex: 0 0 auto;
    min-width: 140px;
    max-width: 140px;
    justify-content: flex-start;
  }

  .quantity-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .action-buttons {
    flex: 1;
    min-width: 0;
  }
}

.out-of-stock:hover {
  transform: none;
}

.out-of-stock .product-image:hover {
  opacity: 1;
}
</style>
