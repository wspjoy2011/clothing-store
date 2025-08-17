<template>
  <div class="cart-page" :class="{ 'dark-theme': isDarkTheme }">
    <v-container class="cart-container">
      <!-- Header Section -->
      <div class="cart-header">
        <v-row align="center" class="mb-6">
          <v-col cols="12" md="8">
            <h1 class="cart-title">
              <v-icon icon="mdi-cart" size="32" class="me-3" color="primary"/>
              Shopping Cart
            </h1>
            <p v-if="hasItems" class="cart-subtitle">
              {{ itemsCount }} {{ itemsCount === 1 ? 'item' : 'items' }} in your cart
            </p>
          </v-col>
          <v-col cols="12" md="4" class="text-md-end">
            <v-btn
                v-if="hasItems"
                variant="outlined"
                color="primary"
                prepend-icon="mdi-refresh"
                @click="handleReloadCart"
                :loading="isLoading"
                class="reload-btn"
            >
              Refresh Cart
            </v-btn>
          </v-col>
        </v-row>
      </div>

      <!-- Initial Loading State -->
      <div v-if="isLoading && !isInitialized" class="loading-section">
        <v-row justify="center" class="py-12">
          <v-col cols="12" class="text-center">
            <v-progress-circular
                color="primary"
                indeterminate
                size="64"
                width="4"
                class="mb-4"
            />
            <h3 class="text-h6 text-medium-emphasis">Loading your cart...</h3>
          </v-col>
        </v-row>
      </div>

      <!-- Error State -->
      <v-alert
          v-if="error && !isLoading"
          type="error"
          variant="tonal"
          class="mb-6"
          closable
          @click:close="error = null"
      >
        <template #title>
          <span class="text-subtitle-1 font-weight-bold">Cart Error</span>
        </template>
        <div class="error-content">
          <p class="mb-2">{{ getCartErrorDetails.message }}</p>
          <div class="error-actions">
            <v-btn
                size="small"
                variant="outlined"
                color="error"
                @click="handleReloadCart"
                :loading="isLoading"
                class="me-2"
            >
              Retry
            </v-btn>
          </div>
        </div>
      </v-alert>

      <!-- Empty Cart State -->
      <div v-if="!hasItems && !isLoading && !error" class="empty-cart">
        <v-row justify="center">
          <v-col cols="12" md="8" lg="6" class="text-center">
            <div class="empty-cart-content">
              <v-icon
                  icon="mdi-cart-outline"
                  size="120"
                  color="primary"
                  class="empty-cart-icon mb-6"
              />
              <h2 class="text-h4 mb-4 font-weight-bold empty-cart-title">Your cart is empty</h2>
              <p class="text-h6 text-medium-emphasis mb-8 empty-cart-description">
                Looks like you haven't added anything to your cart yet.
                Start shopping to fill it up!
              </p>
              <v-btn
                  color="primary"
                  size="large"
                  variant="flat"
                  prepend-icon="mdi-shopping"
                  to="/catalog"
                  class="continue-shopping-btn"
              >
                Continue Shopping
              </v-btn>
            </div>
          </v-col>
        </v-row>
      </div>

      <!-- Cart Content -->
      <div v-if="hasItems" class="cart-content">
        <v-row>
          <!-- Cart Items Section -->
          <v-col cols="12" lg="8">
            <v-card class="cart-items-card" elevation="2">
              <v-card-title class="cart-items-header">
                <v-icon icon="mdi-format-list-bulleted" class="me-2"/>
                Cart Items
              </v-card-title>

              <v-divider/>

              <v-card-text class="pa-0 position-relative">
                <div class="cart-items-list">
                  <div
                      v-for="item in cart.items"
                      :key="item.id"
                      class="cart-item position-relative"
                  >
                    <cart-item-card
                        :item="item"
                        @update:quantity="handleUpdateQuantity"
                        @remove="handleRemoveItem"
                        @view-product="handleViewProduct"
                    />

                    <div v-if="processingItems.has(item.id)" class="item-overlay">
                      <div class="item-overlay-content">
                        <v-progress-circular
                            color="primary"
                            indeterminate
                            size="56"
                            width="5"
                            class="mb-2"
                        />
                        <span class="text-caption text-medium-emphasis">Updating...</span>
                      </div>
                    </div>
                  </div>
                </div>
              </v-card-text>

            </v-card>
          </v-col>

          <!-- Cart Summary Section -->
          <v-col cols="12" lg="4">
            <div class="cart-summary-sticky">
              <v-card class="cart-summary-card" elevation="4">
                <v-card-title class="cart-summary-header">
                  <v-icon icon="mdi-calculator" class="me-2"/>
                  Order Summary
                </v-card-title>

                <v-divider/>

                <v-card-text class="cart-summary-content">
                  <div class="summary-row">
                    <span class="summary-label">Subtotal ({{ itemsCount }} items)</span>
                    <span class="summary-value">${{ formattedTotalAmount }}</span>
                  </div>

                  <div v-if="hasDiscount" class="summary-row discount-row">
                    <span class="summary-label text-success">Discount</span>
                    <span class="summary-value text-success">-${{ formattedTotalDiscount }}</span>
                  </div>

                  <v-divider class="my-4"/>

                  <div class="summary-row total-row">
                    <span class="summary-label">Total</span>
                    <span class="summary-value total-value">${{ formattedFinalAmount }}</span>
                  </div>

                  <div class="checkout-section">
                    <v-btn
                        color="primary"
                        size="large"
                        variant="flat"
                        block
                        prepend-icon="mdi-credit-card"
                        class="checkout-btn"
                        @click="handleCheckout"
                        :disabled="!hasItems"
                    >
                      Proceed to Checkout
                    </v-btn>

                    <v-btn
                        variant="text"
                        size="small"
                        block
                        prepend-icon="mdi-arrow-left"
                        to="/catalog"
                        class="continue-shopping-link mt-3"
                    >
                      Continue Shopping
                    </v-btn>
                  </div>
                </v-card-text>
              </v-card>

              <!-- Security Badge -->
              <div class="security-badge mt-4">
                <v-card variant="tonal" color="success">
                  <v-card-text class="text-center py-3">
                    <v-icon icon="mdi-shield-check" color="success" class="me-2"/>
                    <span class="text-success font-weight-medium">
                      Secure Checkout Guaranteed
                    </span>
                  </v-card-text>
                </v-card>
              </div>
            </div>
          </v-col>
        </v-row>
      </div>

      <!-- Cart Actions Bar (Mobile) -->
      <div v-if="hasItems" class="cart-actions-mobile d-lg-none">
        <v-card class="cart-actions-card" elevation="8">
          <v-card-text class="pa-4">
            <div class="mobile-summary mb-3">
              <div class="mobile-total">
                <span class="total-label">Total: </span>
                <span class="total-amount">${{ formattedFinalAmount }}</span>
              </div>
              <div class="items-count">{{ itemsCount }} items</div>
            </div>
            <v-btn
                color="primary"
                size="large"
                variant="flat"
                block
                prepend-icon="mdi-credit-card"
                @click="handleCheckout"
            >
              Proceed to Checkout
            </v-btn>
          </v-card-text>
        </v-card>
      </div>
    </v-container>
  </div>
</template>

<script setup>
import {useRouter} from 'vue-router'
import {useCartPage} from '@/composables/cart/useCartPage.js'
import CartItemCard from '@/components/cart/CartItemCard.vue'
import {ref} from "vue";

const router = useRouter()

const {
  // Theme
  isDarkTheme,

  // State
  cart,
  isLoading,
  error,
  hasItems,
  itemsCount,
  isInitialized,

  // Actions
  reloadCart,
  removeItemFromCart,

  // Error handling
  getCartErrorDetails,

  // Price formatting
  formattedTotalAmount,
  formattedTotalDiscount,
  formattedFinalAmount,
  hasDiscount
} = useCartPage()

const processingItems = ref(new Set())

const handleReloadCart = async () => {
  try {
    await reloadCart()
  } catch (error) {
    console.error('Failed to reload cart:', error)
  }
}

const handleUpdateQuantity = async (itemId, newQuantity) => {
  try {
    processingItems.value.add(itemId)

    // TODO: Implement update quantity functionality
    console.log(`Update item ${itemId} to quantity ${newQuantity}`)
  } catch (error) {
    console.error('Failed to update quantity:', error)
  }
}

const handleRemoveItem = async (itemId) => {
  processingItems.value.add(itemId)
  try {
    await removeItemFromCart(itemId)
  } catch (error) {
    console.error('Failed to remove item:', error)
  }
}


const handleViewProduct = (productSlug) => {
  router.push({
    name: 'product-detail',
    params: {productSlug}
  })
}

const handleCheckout = () => {
  // TODO: Navigate to checkout page
  console.log('Proceed to checkout')
}
</script>


<style scoped>
/* Light theme styles */
.cart-page {
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  min-height: 100vh;
  padding: 24px 0;
}

.cart-container {
  max-width: 1400px;
}

.cart-header {
  margin-bottom: 32px;
}

.cart-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: #1a1a1a;
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.cart-subtitle {
  font-size: 1.1rem;
  color: #666;
  margin: 0;
}

.reload-btn {
  text-transform: none;
  font-weight: 600;
}

.loading-section {
  background: rgba(255, 255, 255, 0.9);
  border-radius: 16px;
  backdrop-filter: blur(10px);
}

.error-content {
  margin-top: 8px;
}

.error-actions {
  margin-top: 16px;
}

.empty-cart {
  padding: 64px 0;
}

.empty-cart-content {
  background: rgba(255, 255, 255, 0.9);
  border-radius: 24px;
  padding: 48px 32px;
  backdrop-filter: blur(10px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.empty-cart-title {
  color: #1a1a1a;
}

.empty-cart-description {
  color: #666;
}

.empty-cart-icon {
  opacity: 0.6;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-10px);
  }
}

.continue-shopping-btn {
  font-size: 1.1rem;
  font-weight: 600;
  text-transform: none;
  padding: 16px 32px;
  border-radius: 12px;
}

.cart-content {
  gap: 24px;
}

.cart-items-card {
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
}

.cart-items-header {
  font-size: 1.3rem;
  font-weight: 600;
  color: #1a1a1a;
  padding: 20px 24px 16px;
}

.cart-items-list {
  padding: 0;
}

.cart-item {
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}

.cart-item:last-child {
  border-bottom: none;
}

.item-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
  border-radius: 8px;
  backdrop-filter: blur(3px);
}

.item-overlay-content {
  text-align: center;
  min-width: 160px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.cart-summary-sticky {
  position: sticky;
  top: 24px;
}

.cart-summary-card {
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(15px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.cart-summary-header {
  font-size: 1.3rem;
  font-weight: 600;
  color: #1a1a1a;
  padding: 20px 24px 16px;
}

.cart-summary-content {
  padding: 0 24px 24px;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.summary-label {
  font-size: 0.95rem;
  color: #666;
}

.summary-value {
  font-size: 0.95rem;
  font-weight: 600;
  color: #1a1a1a;
}

.discount-row .summary-label,
.discount-row .summary-value {
  color: #2e7d32 !important;
  font-weight: 600;
}

.total-row {
  margin-bottom: 24px;
}

.total-row .summary-label {
  font-size: 1.1rem;
  font-weight: 700;
  color: #1a1a1a;
}

.total-value {
  font-size: 1.3rem;
  font-weight: 700;
  color: #1976d2;
}

.checkout-section {
  margin-top: 24px;
}

.checkout-btn {
  font-size: 1.1rem;
  font-weight: 600;
  text-transform: none;
  padding: 16px;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(25, 118, 210, 0.3);
}

.continue-shopping-link {
  text-transform: none;
  font-weight: 500;
  color: #666;
}

.security-badge {
  border-radius: 12px;
  overflow: hidden;
}

.cart-actions-mobile {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  background: transparent;
  padding: 16px;
}

.cart-actions-card {
  border-radius: 16px 16px 0 0;
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(15px);
}

.mobile-summary {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.mobile-total {
  font-size: 1.1rem;
}

.total-label {
  color: #666;
  font-weight: 500;
}

.total-amount {
  font-weight: 700;
  color: #1976d2;
  font-size: 1.3rem;
}

.items-count {
  font-size: 0.9rem;
  color: #666;
}

/* Dark theme support */
.dark-theme {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
}

.dark-theme .cart-title {
  color: #e8eaed;
}

.dark-theme .cart-subtitle {
  color: #9aa0a6;
}

.dark-theme .loading-section {
  background: rgba(48, 48, 48, 0.9);
}

.dark-theme .empty-cart-content {
  background: rgba(48, 48, 48, 0.9);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.dark-theme .empty-cart-title {
  color: #e8eaed;
}

.dark-theme .empty-cart-description {
  color: #9aa0a6;
}

.dark-theme .cart-items-card {
  background: rgba(48, 48, 48, 0.95);
}

.dark-theme .cart-items-header {
  color: #e8eaed;
}

.dark-theme .cart-item {
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.dark-theme .item-overlay {
  background-color: rgba(18, 18, 18, 0.9);
}

.dark-theme .item-overlay-content {
  background: rgba(48, 48, 48, 0.95);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.dark-theme .cart-summary-card {
  background: rgba(48, 48, 48, 0.98);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.dark-theme .cart-summary-header {
  color: #e8eaed;
}

.dark-theme .summary-label {
  color: #9aa0a6;
}

.dark-theme .summary-value {
  color: #e8eaed;
}

.dark-theme .discount-row .summary-label,
.dark-theme .discount-row .summary-value {
  color: #4caf50 !important;
}

.dark-theme .total-row .summary-label {
  color: #e8eaed;
}

.dark-theme .total-value {
  color: #90caf9;
}

.dark-theme .checkout-btn {
  box-shadow: 0 4px 16px rgba(144, 202, 249, 0.2);
}

.dark-theme .continue-shopping-link {
  color: #9aa0a6;
}

.dark-theme .cart-actions-card {
  background: rgba(48, 48, 48, 0.98);
}

.dark-theme .total-label {
  color: #9aa0a6;
}

.dark-theme .total-amount {
  color: #90caf9;
}

.dark-theme .items-count {
  color: #9aa0a6;
}

/* Responsive adjustments */
@media (max-width: 960px) {
  .cart-title {
    font-size: 2rem;
  }

  .cart-summary-sticky {
    position: static;
  }

  .empty-cart-content {
    padding: 32px 24px;
  }

  .cart-page {
    padding: 16px 0 100px;
  }
}

@media (max-width: 600px) {
  .cart-title {
    font-size: 1.75rem;
    flex-direction: column;
    align-items: flex-start;
  }

  .cart-title v-icon {
    margin-bottom: 8px;
  }

  .empty-cart-content {
    padding: 24px 16px;
  }

  .empty-cart-icon {
    font-size: 80px;
  }
}
</style>
