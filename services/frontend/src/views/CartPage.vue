<template>
  <div class="cart-page" :class="{ 'dark-theme': isDarkTheme }">
    <v-container class="cart-container">
      <!-- Header Section -->
      <CartHeader
          :has-items="hasItems"
          :items-count="itemsCount"
          :is-loading="isLoading"
          @refresh="handleReloadCart"
      />

      <!-- Initial Loading State -->
      <CartLoading v-if="isLoading && !isInitialized"/>

      <!-- Error State -->
      <CartErrorAlert
          v-if="error && !isLoading"
          :message="errorMessage"
          :is-loading="isLoading"
          @retry="handleReloadCart"
          @clear="error = null"
      />

      <!-- Empty Cart State -->
      <CartEmptyState v-if="!hasItems && !isLoading && !error"/>

      <!-- Cart Content -->
      <div v-if="hasItems" class="cart-content">
        <v-row>
          <!-- Cart Items Section -->
          <v-col cols="12" lg="8">
            <CartItemsList
                :cart="cart"
                :processing-ids="processingItems"
                :max-available-by-id="maxAvailableByItemId"
                @update-quantity="handleUpdateQuantity"
                @remove-item="handleRemoveItem"
                @view-product="handleViewProduct"
            />
          </v-col>

          <!-- Cart Summary Section -->
          <v-col cols="12" lg="4">
            <CartSummary
                :items-count="itemsCount"
                :has-discount="hasDiscount"
                :formatted-total-amount="formattedTotalAmount"
                :formatted-total-discount="formattedTotalDiscount"
                :formatted-final-amount="formattedFinalAmount"
                :has-items="hasItems"
                @checkout="handleCheckout"
            />
          </v-col>
        </v-row>
      </div>

      <!-- Cart Actions Bar (Mobile) -->
      <CartActionsMobile
          v-if="hasItems"
          :formatted-final-amount="formattedFinalAmount"
          :items-count="itemsCount"
          @checkout="handleCheckout"
      />
    </v-container>
  </div>
</template>

<script setup>
import {ref, onMounted, watch, computed} from "vue"
import {useRouter} from 'vue-router'
import {useCartPage} from '@/composables/cart/useCartPage.js'
import {useNotifications} from '@/composables/accounts/useNotifications.js'
import {useCatalogStore} from '@/stores/catalog'

import CartHeader from '@/components/cart/page/CartHeader.vue'
import CartLoading from '@/components/cart/page/CartLoading.vue'
import CartErrorAlert from '@/components/cart/page/CartErrorAlert.vue'
import CartEmptyState from '@/components/cart/page/CartEmptyState.vue'
import CartItemsList from '@/components/cart/page/CartItemsList.vue'
import CartSummary from '@/components/cart/page/CartSummary.vue'
import CartActionsMobile from '@/components/cart/page/CartActionsMobile.vue'

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
  updateItemInCart,

  // Error handling
  getCartErrorDetails,

  // Price formatting
  formattedTotalAmount,
  formattedTotalDiscount,
  formattedFinalAmount,
  hasDiscount
} = useCartPage()

const errorMessage = computed(() => getCartErrorDetails.message)

const {showWarning, showError} = useNotifications()
const catalogStore = useCatalogStore()

const processingItems = ref(new Set())
const maxAvailableByItemId = ref(new Map())

const fetchAndSetMaxAvailable = async (cartItem) => {
  try {
    const product = await catalogStore.getProductById(cartItem.product_id)
    const inv = product?.inventory
    const maxAvailable = typeof inv?.available_quantity === 'number' ? inv.available_quantity : null
    maxAvailableByItemId.value.set(cartItem.id, maxAvailable)
  } catch (e) {
    maxAvailableByItemId.value.set(cartItem.id, null)
  }
}

const preloadMaxAvailable = async () => {
  const items = cart.value?.items || []
  await Promise.all(items.map(item => fetchAndSetMaxAvailable(item)))
}

onMounted(preloadMaxAvailable)

watch(
    () => cart.value?.items?.map(i => i.id),
    () => {
      preloadMaxAvailable()
    }
)

const handleReloadCart = async () => {
  try {
    await reloadCart()
  } catch (e) {
    showError('Failed to reload cart')
  }
}

const handleUpdateQuantity = async (itemId, newQuantity) => {
  processingItems.value.add(itemId)
  try {
    const currentItem = cart.value?.items?.find(i => i.id === itemId)
    if (!currentItem) {
      showError('Item not found in cart')
      return
    }
    if (currentItem.is_available === false) {
      showWarning('This item is currently unavailable')
      return
    }
    let maxAvailable = maxAvailableByItemId.value.get(itemId)
    if (maxAvailable == null) {
      await fetchAndSetMaxAvailable(currentItem)
      maxAvailable = maxAvailableByItemId.value.get(itemId)
    }
    const minQty = 1
    let desiredQty = Number(newQuantity)
    if (!Number.isFinite(desiredQty)) desiredQty = minQty
    desiredQty = Math.max(minQty, desiredQty)
    if (typeof maxAvailable === 'number' && desiredQty > maxAvailable) {
      desiredQty = maxAvailable
      showWarning(`Only ${maxAvailable} pcs available for this item`)
    }
    if (desiredQty === currentItem.quantity) {
      return
    }
    await updateItemInCart(itemId, {quantity: desiredQty})
  } catch (e) {
    showError(e?.message || 'Failed to update item quantity')
  } finally {
    processingItems.value.delete(itemId)
  }
}

const handleRemoveItem = async (itemId) => {
  processingItems.value.add(itemId)
  try {
    await removeItemFromCart(itemId)
  } catch (e) {
    showError(e?.message || 'Failed to remove item from cart')
  } finally {
    processingItems.value.delete(itemId)
  }
}

const handleViewProduct = (productSlug) => {
  router.push({name: 'product-detail', params: {productSlug}})
}

const handleCheckout = () => {
  // TODO: Navigate to checkout page
}
</script>

<style scoped>
.cart-page {
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  min-height: 100vh;
  padding: 24px 0;
}

.cart-container {
  max-width: 1400px;
}

.cart-content {
  gap: 24px;
}

/* Dark theme support */
.dark-theme {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
}

/* Responsive adjustments */
@media (max-width: 960px) {
  .cart-page {
    padding: 16px 0 100px;
  }
}
</style>
