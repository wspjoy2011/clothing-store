<template>
  <v-card
    :class="['mx-auto my-3 product-card', { 'out-of-stock': !isAvailable }]"
    :elevation="hover ? 8 : 2"
    @mouseenter="hover = true"
    @mouseleave="hover = false"
  >
    <!-- Main image & overlays -->
    <div class="position-relative">
      <div v-if="imageLoading" class="image-loader">
        <v-progress-circular color="primary" indeterminate size="30" />
      </div>

      <!-- Product image  -->
      <v-img
        :src="props.product.image_url"
        height="250"
        cover
        class="product-image"
        @load="imageLoaded"
        @error="imageLoaded"
      />

      <!-- Notification -->
      <ClothesCardNotification
        :active="activeNotification"
        :type="notificationType"
        :text="notificationText"
        :progress="progress"
        :close="closeNotification"
        :color="notificationColor"
      />

      <div v-if="!isAvailable" class="out-of-stock-overlay">
        <v-chip
          color="error"
          variant="elevated"
          size="large"
          class="font-weight-bold"
        >Out of Stock</v-chip>
      </div>

      <div v-if="isAvailable && !productInCart" class="stock-badge">
        <v-chip
          color="success"
          variant="elevated"
          size="small"
          class="font-weight-medium"
        >{{ availableQuantity }} in stock</v-chip>
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

    <!-- Title -->
    <v-card-title class="text-subtitle-1 font-weight-bold d-block text-truncate">
      {{ props.product.product_display_name }}
    </v-card-title>

    <!-- Subtitle -->
    <v-card-subtitle>
      <span class="font-weight-medium">{{ props.product.gender }}</span>
      <span class="ms-2 text-medium-emphasis text-caption">{{ props.product.year }}</span>
    </v-card-subtitle>

    <!-- Price section -->
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

    <!-- Actions row -->
    <v-card-actions class="px-3 pb-3">
      <div class="card-controls">
        <div v-if="isAvailable && !productInCart" class="quantity-section">
          <ClothesQuantityControl
            :quantity="quantity"
            :available-quantity="availableQuantity"
            :decrease="decreaseQuantity"
            :increase="increaseQuantity"
          />
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
            @click.stop="handleAddToCart"
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
            @click.stop="handleRemoveFromCart"
          >
            <v-icon start>mdi-cart-remove</v-icon>
            {{ isRemovingItem ? 'Removing...' : 'Remove from Cart' }}
          </v-btn>

          <!-- View detail navigation -->
          <v-btn
            :disabled="!isAvailable"
            :color="getActionButtonColor()"
            variant="outlined"
            class="text-none view-details-btn"
            block
            @click.stop="handleViewProductDetail"
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
import { ref, toRef } from 'vue'
import { useProductInventory } from '@/composables/product/useProductInventory'
import { useCart } from '@/composables/cart/useCart.js'
import ClothesCardNotification from '@/components/catalog/ClothesCardNotification.vue'
import ClothesQuantityControl from '@/components/catalog/ClothesQuantityControl.vue'
import { useCardNotification } from '@/composables/catalog/useCardNotification.js'
import { useCardQuantity } from '@/composables/catalog/useCardQuantity.js'
import { useNavigation } from '@/composables/accounts/useNavigation.js'

const props = defineProps({
  product: {
    type: Object,
    required: true
  }
})

const hover = ref(false)

const productRef = toRef(props, 'product')

const {
  isAvailable,
  hasDiscount,
  formattedBasePrice,
  formattedSalePrice,
  getActionButtonText,
  getActionButtonColor
} = useProductInventory(productRef)

const {
  isAddingItem,
  isRemovingItem,
  addItemToCart,
  removeItemFromCart,
  isProductInCart,
  getCartItemDisplayInfo,
  getCartItemInfo
} = useCart()

const productInCart = isProductInCart(props.product.product_id)
const cartDisplayInfo = getCartItemDisplayInfo(props.product.product_id)

const {
  quantity,
  availableQuantity,
  imageLoading,
  imageLoaded,
  increaseQuantity,
  decreaseQuantity
} = useCardQuantity(props.product)

const {
  notificationType,
  notificationText,
  activeNotification,
  progress,
  notificationColor,
  closeNotification,
  showAddSuccess,
  showRemoveSuccess,
  showError,
  showWarning
} = useCardNotification()

const {goToProductDetail} = useNavigation()

const handleAddToCart = async () => {
  if (!isAvailable.value || isAddingItem.value || productInCart.value) return
  try {
    await addItemToCart({
      product_id: props.product.product_id,
      quantity: quantity.value
    })
    quantity.value = 1
    showAddSuccess()
  } catch (error) {
    showError(error?.message || 'Failed to add item to cart')
  }
}

const handleRemoveFromCart = async () => {
  if (!productInCart.value || isRemovingItem.value) return
  try {
    const cartItem = getCartItemInfo(props.product.product_id).value
    if (!cartItem) {
      showWarning('Cart item not found for this product')
      return
    }
    await removeItemFromCart(cartItem.id)
    showRemoveSuccess()
  } catch (error) {
    showError(error?.message || 'Failed to remove item from cart')
  }
}

const handleViewProductDetail = () => {
  if (!isAvailable.value) return
  goToProductDetail(props.product.slug)
}
</script>

<style scoped>
.notification-box {
  position: relative;
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
