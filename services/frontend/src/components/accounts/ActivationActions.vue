<template>
  <div class="activation-actions">
    <!-- Success Actions -->
    <template v-if="activationSuccess">
      <v-btn
          color="primary"
          size="large"
          class="action-btn"
          @click="$emit('go-login')"
      >
        <v-icon start icon="mdi-login"/>
        Sign In Now
      </v-btn>

      <v-btn
          variant="outlined"
          size="large"
          class="action-btn mt-3"
          @click="$emit('go-home')"
      >
        <v-icon start icon="mdi-home"/>
        Go to Homepage
      </v-btn>
    </template>

    <!-- Error Actions -->
    <template v-else-if="hasError">
      <v-btn
          v-if="errorDetails.canRetry"
          color="primary"
          size="large"
          class="action-btn"
          @click="$emit('retry')"
      >
        <v-icon start icon="mdi-refresh"/>
        Try Again
      </v-btn>

      <v-btn
          v-if="errorDetails.showResend"
          color="warning"
          size="large"
          class="action-btn"
          :class="{ 'mt-3': errorDetails.canRetry }"
          @click="$emit('resend')"
      >
        <v-icon start icon="mdi-email-refresh"/>
        Resend Activation Email
      </v-btn>

      <v-btn
          v-if="errorDetails.showRegister"
          variant="outlined"
          size="large"
          class="action-btn"
          :class="{ 'mt-3': errorDetails.canRetry || errorDetails.showResend }"
          @click="$emit('go-register')"
      >
        <v-icon start icon="mdi-account-plus"/>
        Register New Account
      </v-btn>

      <v-btn
          variant="outlined"
          size="large"
          class="action-btn"
          :class="{ 'mt-3': errorDetails.canRetry || errorDetails.showRegister || errorDetails.showResend }"
          @click="$emit('go-home')"
      >
        <v-icon start icon="mdi-home"/>
        Go to Homepage
      </v-btn>
    </template>

    <!-- Invalid Link Actions -->
    <template v-else>
      <v-btn
          color="primary"
          size="large"
          class="action-btn"
          @click="$emit('go-register')"
      >
        <v-icon start icon="mdi-account-plus"/>
        Register Account
      </v-btn>

      <v-btn
          variant="outlined"
          size="large"
          class="action-btn mt-3"
          @click="$emit('go-home')"
      >
        <v-icon start icon="mdi-home"/>
        Go to Homepage
      </v-btn>
    </template>
  </div>
</template>

<script setup>
defineProps({
  activationSuccess: {
    type: Boolean,
    default: false
  },
  hasError: {
    type: Boolean,
    default: false
  },
  errorDetails: {
    type: Object,
    default: () => ({})
  }
});

defineEmits(['go-login', 'go-home', 'go-register', 'retry', 'resend']);
</script>

<style scoped>
.activation-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 0 24px 24px;
}

.action-btn {
  border-radius: 12px;
  font-weight: 600;
  text-transform: none;
  letter-spacing: 0.025em;
  transition: all 0.3s ease;
}

.action-btn:hover {
  transform: translateY(-2px);
}

@media (max-width: 600px) {
  .activation-actions {
    padding: 0 16px 16px;
  }
}
</style>
