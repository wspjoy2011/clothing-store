<template>
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
          <CartItemCard
              :item="item"
              :max-available="maxAvailableById.get(item.id) ?? undefined"
              @update:quantity="(id, qty) => $emit('update-quantity', id, qty)"
              @remove="$emit('remove-item', item.id)"
              @view-product="$emit('view-product', $event)"
          />

          <div v-if="processingIds.has(item.id)" class="item-overlay">
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
</template>

<script setup>
import CartItemCard from '@/components/cart/CartItemCard.vue'

const props = defineProps({
  cart: {type: Object, required: true},
  processingIds: {type: Object, required: true}, // Set
  maxAvailableById: {type: Object, required: true} // Map
})
defineEmits(['update-quantity', 'remove-item', 'view-product'])
</script>

<style scoped>
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
  inset: 0;
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

/* Dark theme support */
:deep(.dark-theme) .cart-items-card {
  background: rgba(48, 48, 48, 0.95);
}

:deep(.dark-theme) .cart-items-header {
  color: #e8eaed;
}

:deep(.dark-theme) .cart-item {
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

:deep(.dark-theme) .item-overlay {
  background-color: rgba(18, 18, 18, 0.9);
}

:deep(.dark-theme) .item-overlay-content {
  background: rgba(48, 48, 48, 0.95);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}
</style>
