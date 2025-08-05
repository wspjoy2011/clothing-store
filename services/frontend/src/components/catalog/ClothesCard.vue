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

      <transition name="fade">
        <div
            v-if="activeNotification"
            class="floating-notification"
            :class="notificationType"
        >
          <v-icon class="notif-icon" size="22">
            {{
              notificationType === 'success'
                  ? 'mdi-check-circle'
                  : notificationType === 'error'
                      ? 'mdi-alert-circle'
                      : 'mdi-alert'
            }}
          </v-icon>
          <span class="notif-text">{{ notificationText }}</span>
          <div class="notif-progress-bar">
            <div
                class="notif-progress"
                :style="{ width: progress + '%', background: progressColor }"
            ></div>
          </div>
          <v-btn icon class="notif-close-btn" size="x-small" @click="closeNotification">
            <v-icon size="18">mdi-close</v-icon>
          </v-btn>
        </div>
      </transition>

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
      <div v-if="isAvailable && !productInCart" class="stock-badge">
        <v-chip
            color="success"
            variant="elevated"
            size="small"
            class="font-weight-medium"
        >{{ availableQuantity }} in stock
        </v-chip>
      </div>
      <div v-if="productInCart" class="cart-badge">
        <v-chip
            color="success"
            variant="elevated"
            size="small"
            class="font-weight-bold"
        >
          <v-icon start size="16">mdi-check-circle</v-icon>
          In Cart ({{ cartDisplayInfo.quantity }})
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
    <v-card-text v-if="product.inventory" class="py-2">
      <div class="price-section">
        <div v-if="hasDiscount" class="price-container price-inline">
          <span class="original-price">{{ formattedBasePrice }}</span>
          <span class="sale-price">{{ formattedSalePrice }}</span>
        </div>
        <div v-else class="price-container">
          <span class="base-price">{{ formattedBasePrice }}</span>
        </div>
      </div>
    </v-card-text>
    <v-card-actions class="px-3 pb-3">
      <div class="card-controls">
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
        <div v-if="productInCart" class="in-cart-indicator">
          <v-icon color="success" size="24">mdi-check-circle</v-icon>
          <span class="in-cart-text">
            {{ cartDisplayInfo.displayText }}
          </span>
        </div>
        <div class="action-buttons">
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
          <v-btn
              v-if="productInCart"
              :loading="isRemovingItem"
              :disabled="isRemovingItem"
              color="error"
              variant="flat"
              class="text-none remove-from-cart-btn"
              block
              @click="handleRemoveFromCart"
          >
            <v-icon start>mdi-cart-remove</v-icon>
            {{ isRemovingItem ? 'Removing...' : 'Remove from Cart' }}
          </v-btn>
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
  </v-card>
</template>

<script setup>
import {ref, toRef, computed, watch} from 'vue';
import {useRouter} from 'vue-router';
import {useProductInventory} from '@/composables/product/useProductInventory';
import {useCart} from '@/composables/cart/useCart.js';
import {useNotifications} from '@/composables/accounts/useNotifications.js';

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

const {
  showSuccess, showError, showWarning,
  showSuccessMessage, showErrorMessage, showWarningMessage,
  successMessage, errorMessage, warningMessage,
  hideSuccess, hideError, hideWarning
} = useNotifications();

const notificationType = ref(null);
const notificationText = ref('');
const activeNotification = ref(false);
const progress = ref(100);
const progressInterval = ref(null);

const progressColor = computed(() =>
    notificationType.value === 'error'
        ? '#d32f2f'
        : notificationType.value === 'warning'
            ? '#f9a825'
            : '#43a047'
);

watch(
    [showSuccessMessage, showErrorMessage, showWarningMessage],
    ([succ, err, warn]) => {
      if (succ) {
        notificationText.value = successMessage.value;
        notificationType.value = 'success';
        runProgressBar(3000);
      } else if (err) {
        notificationText.value = errorMessage.value;
        notificationType.value = 'error';
        runProgressBar(5000);
      } else if (warn) {
        notificationText.value = warningMessage.value;
        notificationType.value = 'warning';
        runProgressBar(4000);
      } else {
        activeNotification.value = false;
      }
    }
);

function runProgressBar(duration) {
  activeNotification.value = true;
  progress.value = 100;
  if (progressInterval.value) clearInterval(progressInterval.value);
  const step = 100 / (duration / 40);
  progressInterval.value = setInterval(() => {
    progress.value -= step;
    if (progress.value <= 0) {
      progress.value = 0;
      activeNotification.value = false;
      clearInterval(progressInterval.value);
    }
  }, 40);
}

function closeNotification() {
  activeNotification.value = false;
  hideSuccess();
  hideError();
  hideWarning();
  if (progressInterval.value) clearInterval(progressInterval.value);
}

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
  isRemovingItem,
  addItemToCart,
  removeItemFromCart,
  isProductInCart,
  getCartItemDisplayInfo,
  getCartItemInfo
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
    showSuccess('Product added');
  } catch (error) {
    showError(error?.message || 'Failed to add item to cart');
  }
};

const handleRemoveFromCart = async () => {
  if (!productInCart.value || isRemovingItem.value) return;
  try {
    const cartItem = getCartItemInfo(props.product.product_id).value;
    if (!cartItem) {
      showWarning('Cart item not found for this product');
      return;
    }
    await removeItemFromCart(cartItem.id);
    showSuccess('Product removed');
  } catch (error) {
    showError(error?.message || 'Failed to remove item from cart');
  }
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
.notification-box {
  position: relative;
}

.floating-notification {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  margin: 0 auto;
  z-index: 10;
  min-width: 0;
  width: 100%;
  max-width: 100%;
  height: 48px;
  padding: 12px 16px 12px 44px;
  border-radius: 12px 12px 0 0;
  box-shadow: 0 4px 32px rgba(80, 80, 80, 0.13);
  font-size: 1rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  background: #fff;
  color: #2e7d32;
  opacity: 0.97;
  animation: fadein-notif 0.22s;
  pointer-events: auto;
}

.floating-notification.success {
  border-left: 5px solid #43a047;
}

.floating-notification.error {
  border-left: 5px solid #d32f2f;
  color: #d32f2f;
}

.floating-notification.warning {
  border-left: 5px solid #f9a825;
  color: #a68104;
}

.floating-notification .notif-icon {
  position: absolute;
  left: 14px;
  top: 14px;
}

.floating-notification .notif-text {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.floating-notification .notif-close-btn {
  margin-left: 10px;
}

.floating-notification .notif-progress-bar {
  margin: 0;
  padding: 0;
  width: 100%;
  height: 3px;
  border-radius: 0 0 2px 2px;
  background: #e0e0e0;
  position: absolute;
  left: 0;
  bottom: 0;
  overflow: hidden;
}

.floating-notification .notif-progress {
  height: 100%;
  transition: width 30ms linear;
}

@keyframes fadein-notif {
  from {
    opacity: 0;
    transform: translateY(-70%);
  }
  to {
    opacity: 0.97;
    transform: translateY(0%);
  }
}

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
}

.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 8px;
  width: 100%;
}

.in-cart-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background-color: rgba(76, 175, 80, 0.1);
  border-radius: 8px;
  border: 1px solid rgba(76, 175, 80, 0.3);
}

.in-cart-text {
  font-weight: bold;
  color: #2e7d32;
  font-size: 0.875rem;
}

.add-to-cart-btn {
  transition: all 0.2s ease;
}

.add-to-cart-btn:hover {
  transform: translateY(-1px);
}

.remove-from-cart-btn {
  transition: all 0.2s ease;
}

.remove-from-cart-btn:hover {
  transform: translateY(-1px);
}

.view-details-btn {
  transition: all 0.2s ease;
}

.view-details-btn:hover {
  transform: translateY(-1px);
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

@media (max-width: 600px) {
  .product-card {
    margin: 8px auto;
  }

  .card-controls {
    gap: 12px;
  }

  .quantity-controls {
    gap: 8px;
  }

  .action-buttons {
    gap: 6px;
  }

  .in-cart-indicator {
    padding: 10px 12px;
  }

  .in-cart-text {
    font-size: 0.85rem;
  }
}
</style>
