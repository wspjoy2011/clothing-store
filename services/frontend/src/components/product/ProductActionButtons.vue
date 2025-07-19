<template>
  <div class="action-buttons">
    <v-btn
        :disabled="!canAddToCart"
        :color="getActionButtonColor()"
        size="large"
        variant="flat"
        block
        class="mb-3"
        prepend-icon="mdi-cart-plus"
        @click="handleAddToCart"
    >
      {{ getActionButtonText() }}
    </v-btn>

    <v-btn
        :disabled="!isAvailable"
        :color="getActionButtonColor('secondary')"
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
import {toRef} from 'vue';
import {useProductInventory} from '@/composables/product/useProductInventory';

const props = defineProps({
  product: {
    type: Object,
    required: true
  }
});

const emit = defineEmits(['go-back', 'add-to-cart', 'add-to-wishlist']);

const productRef = toRef(props, 'product');
const {
  isAvailable,
  canAddToCart,
  getActionButtonText,
  getActionButtonColor
} = useProductInventory(productRef);

const handleAddToCart = () => {
  if (!canAddToCart.value) return;
  emit('add-to-cart');
  // TODO: Implement cart functionality
};

const handleAddToWishlist = () => {
  if (!isAvailable.value) return;
  emit('add-to-wishlist');
  // TODO: Implement wishlist functionality
};
</script>

<style scoped>
.action-buttons {
  margin-top: auto;
}
</style>
