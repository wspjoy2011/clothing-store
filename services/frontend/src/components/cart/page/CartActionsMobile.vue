<template>
  <div class="cart-actions-mobile d-lg-none">
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
            @click="$emit('checkout')"
        >
          Proceed to Checkout
        </v-btn>
      </v-card-text>
    </v-card>
  </div>
</template>

<script setup>
const props = defineProps({
  formattedFinalAmount: {type: [String, Number], default: ''},
  itemsCount: {type: Number, default: 0}
})
defineEmits(['checkout'])
</script>

<style scoped>
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

:deep(.dark-theme) .cart-actions-card {
  background: rgba(48, 48, 48, 0.98);
}

:deep(.dark-theme) .total-label {
  color: #9aa0a6;
}

:deep(.dark-theme) .total-amount {
  color: #90caf9;
}

:deep(.dark-theme) .items-count {
  color: #9aa0a6;
}
</style>
