<template>
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
              @click="$emit('checkout')"
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
</template>

<script setup>
const props = defineProps({
  itemsCount: {type: Number, default: 0},
  hasDiscount: {type: Boolean, default: false},
  formattedTotalAmount: {type: [String, Number], default: ''},
  formattedTotalDiscount: {type: [String, Number], default: ''},
  formattedFinalAmount: {type: [String, Number], default: ''},
  hasItems: {type: Boolean, default: false}
})
defineEmits(['checkout'])
</script>

<style scoped>
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

.discount-row .summary-label, .discount-row .summary-value {
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

:deep(.dark-theme) .cart-summary-card {
  background: rgba(48, 48, 48, 0.98);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

:deep(.dark-theme) .cart-summary-header {
  color: #e8eaed;
}

:deep(.dark-theme) .summary-label {
  color: #9aa0a6;
}

:deep(.dark-theme) .summary-value {
  color: #e8eaed;
}

:deep(.dark-theme) .discount-row .summary-label, :deep(.dark-theme) .discount-row .summary-value {
  color: #4caf50 !important;
}

:deep(.dark-theme) .total-row .summary-label {
  color: #e8eaed;
}

:deep(.dark-theme) .total-value {
  color: #90caf9;
}

:deep(.dark-theme) .checkout-btn {
  box-shadow: 0 4px 16px rgba(144, 202, 249, 0.2);
}
</style>
