<template>
  <div class="action-buttons">
    <v-btn
        :disabled="!isAvailable"
        :color="isAvailable ? 'primary' : 'grey'"
        size="large"
        variant="flat"
        block
        class="mb-3"
        prepend-icon="mdi-cart-plus"
        @click="handleAddToCart"
    >
      {{ isAvailable ? 'Add to Cart' : 'Out of Stock' }}
    </v-btn>

    <v-btn
        :disabled="!isAvailable"
        :color="isAvailable ? 'secondary' : 'grey'"
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
import {computed} from 'vue';

const props = defineProps({
  product: {
    type: Object,
    required: true
  }
});

const emit = defineEmits(['go-back', 'add-to-cart', 'add-to-wishlist']);

const isAvailable = computed(() =>
    props.product.inventory?.is_in_stock && props.product.inventory?.is_active
);

const handleAddToCart = () => {
  if (!isAvailable.value) return;
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
