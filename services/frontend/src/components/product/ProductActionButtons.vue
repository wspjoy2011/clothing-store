<template>
  <div class="action-buttons">
    <v-btn
        color="primary"
        size="large"
        variant="flat"
        block
        class="mb-3"
        prepend-icon="mdi-cart-plus"
        @click="handleAddToCart"
    >
      Add to Cart
    </v-btn>

    <v-btn
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
const emit = defineEmits(['go-back', 'add-to-cart', 'add-to-wishlist']);

const handleAddToCart = () => {
  emit('add-to-cart');
  // TODO: Implement cart functionality
};

const handleAddToWishlist = () => {
  emit('add-to-wishlist');
  // TODO: Implement wishlist functionality
};
</script>

<style scoped>
.action-buttons {
  margin-top: auto;
}
</style>
