<template>
  <div class="action-buttons">
    <v-btn
      :disabled="!isAvailable || isAddingItem || isRemovingItem"
      :color="cartButtonColor"
      size="large"
      variant="flat"
      block
      class="mb-3"
      :prepend-icon="cartButtonIcon"
      @click="handleCartAction"
    >
      {{ cartButtonText }}
    </v-btn>

    <v-btn
      :disabled="!isAvailable"
      color="secondary"
      size="large"
      variant="outlined"
      block
      class="mb-3"
      prepend-icon="mdi-heart-outline"
      @click="handleAddToWishlist"
    >
      Add to Wishlist
    </v-btn>

    <v-btn
      color="primary"
      variant="text"
      block
      @click="$emit('go-back')"
      prepend-icon="mdi-arrow-left"
    >
      Back to Catalog
    </v-btn>
  </div>
</template>

<script setup>
import { computed, toRef } from 'vue'
import { useProductInventory } from '@/composables/product/useProductInventory'
import { useCart } from '@/composables/cart/useCart'

const props = defineProps({
  product: {
    type: Object,
    required: true
  }
})
const emit = defineEmits(['go-back', 'add-to-wishlist', 'add-to-cart', 'remove-from-cart'])

const productRef = toRef(props, 'product')
const {
  isAvailable
} = useProductInventory(productRef)

const {
  isAddingItem,
  isRemovingItem,
  addItemToCart,
  removeItemFromCart,
  isProductInCart,
  getCartItemInfo
} = useCart({ showNotifications: true })

const inCart = isProductInCart(props.product.product_id)
const cartItemInfo = getCartItemInfo(props.product.product_id)

const cartButtonText = computed(() => (inCart.value ? 'Remove from Cart' : 'Add to Cart'))
const cartButtonColor = computed(() => (inCart.value ? 'error' : 'primary'))
const cartButtonIcon = computed(() => (inCart.value ? 'mdi-cart-remove' : 'mdi-cart-plus'))

const handleCartAction = async () => {
  if (!isAvailable.value) return

  if (inCart.value) {
    const itemId = cartItemInfo.value?.id
    if (!itemId) return
    await removeItemFromCart(itemId)
    emit('remove-from-cart', { productId: props.product.product_id, cartItemId: itemId })
  } else {
    await addItemToCart({ product_id: props.product.product_id, quantity: 1 })
    emit('add-to-cart', { productId: props.product.product_id, quantity: 1 })
  }
}

const handleAddToWishlist = () => {
  if (!isAvailable.value) return
  emit('add-to-wishlist', { productId: props.product.product_id })
}
</script>

<style scoped>
.action-buttons {
  margin-top: auto;
}
</style>
