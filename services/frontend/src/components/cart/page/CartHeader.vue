<template>
  <div class="cart-header">
    <v-row align="center" class="mb-6">
      <v-col cols="12" md="4" class="d-none d-md-block"></v-col>

      <v-col cols="12" md="4" class="text-center">
        <h1 class="cart-title d-inline-flex align-center">
          <v-icon icon="mdi-cart" size="32" class="me-3" color="primary"/>
          Shopping Cart
        </h1>
        <p v-if="hasItems" class="cart-subtitle">
          {{ itemsCount }} {{ itemsCount === 1 ? 'item' : 'items' }} in your cart
        </p>
      </v-col>

      <v-col cols="12" md="4" class="text-md-end text-center mt-3 mt-md-0">
        <v-btn
            v-if="hasItems"
            variant="outlined"
            color="primary"
            prepend-icon="mdi-refresh"
            @click="$emit('refresh')"
            :loading="isLoading"
            class="reload-btn"
        >
          Refresh Cart
        </v-btn>
      </v-col>
    </v-row>
  </div>
</template>

<script setup>
const props = defineProps({
  hasItems: {type: Boolean, default: false},
  itemsCount: {type: Number, default: 0},
  isLoading: {type: Boolean, default: false}
})
defineEmits(['refresh'])
</script>

<style scoped>
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

@media (max-width: 960px) {
  .cart-title {
    font-size: 2rem;
  }
}

@media (max-width: 600px) {
  .cart-title {
    font-size: 1.75rem;
    flex-direction: column;
    align-items: flex-start;
  }

  .cart-title :deep(.v-icon) {
    margin-bottom: 8px;
  }
}
</style>
