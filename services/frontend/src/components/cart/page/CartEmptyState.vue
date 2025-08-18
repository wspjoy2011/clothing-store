<template>
  <div class="empty-cart">
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
</template>

<script setup>
</script>

<style scoped>
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

.continue-shopping-btn {
  font-size: 1.1rem;
  font-weight: 600;
  text-transform: none;
  padding: 16px 32px;
  border-radius: 12px;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-10px);
  }
}

:deep(.dark-theme) .empty-cart-content {
  background: rgba(48, 48, 48, 0.9);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

:deep(.dark-theme) .empty-cart-title {
  color: #e8eaed;
}

:deep(.dark-theme) .empty-cart-description {
  color: #9aa0a6;
}
</style>
