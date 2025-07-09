<template>
  <div v-if="isLoading" class="activation-status">
    <div class="status-content">
      <v-progress-circular
          indeterminate
          size="64"
          color="primary"
          class="mb-4"
      />
      <h2 class="status-title">Activating Account</h2>
      <p class="status-subtitle">Please wait while we activate your account...</p>
    </div>
  </div>

  <div v-else-if="activationSuccess" class="activation-status">
    <div class="status-content">
      <v-icon
          icon="mdi-check-circle"
          size="64"
          color="success"
          class="success-icon mb-4"
      />
      <h2 class="status-title">Account Activated!</h2>
      <p class="status-subtitle">
        Your account has been successfully activated.
        You can now sign in and start shopping.
      </p>
    </div>
  </div>

  <div v-else-if="hasError" class="activation-status">
    <div class="status-content">
      <v-icon
          :icon="errorDetails.icon"
          size="64"
          color="error"
          class="error-icon mb-4"
      />
      <h2 class="status-title">{{ errorDetails.title }}</h2>
      <p class="status-subtitle">{{ errorMessage }}</p>
    </div>
  </div>

  <div v-else class="activation-status">
    <div class="status-content">
      <v-icon
          icon="mdi-link-off"
          size="64"
          color="warning"
          class="warning-icon mb-4"
      />
      <h2 class="status-title">Invalid Activation Link</h2>
      <p class="status-subtitle">
        The activation link is missing required parameters.
        Please check your email and click the activation link again.
      </p>
    </div>
  </div>
</template>

<script setup>
defineProps({
  isLoading: {
    type: Boolean,
    default: false
  },
  activationSuccess: {
    type: Boolean,
    default: false
  },
  hasError: {
    type: Boolean,
    default: false
  },
  errorMessage: {
    type: String,
    default: ''
  },
  errorDetails: {
    type: Object,
    default: () => ({})
  }
});
</script>

<style scoped>
.activation-status {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  padding: 40px 24px;
}

.status-content {
  text-align: center;
  max-width: 400px;
}

.status-title {
  font-size: 1.75rem;
  font-weight: 600;
  margin: 0 0 16px;
  color: inherit;
}

.status-subtitle {
  font-size: 1rem;
  opacity: 0.8;
  margin: 0 0 32px;
  line-height: 1.5;
}

.success-icon {
  animation: checkmark 0.6s ease-in-out;
}

.error-icon,
.warning-icon {
  animation: shake 0.6s ease-in-out;
}

@keyframes checkmark {
  0% {
    transform: scale(0);
    opacity: 0;
  }
  50% {
    transform: scale(1.2);
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

@keyframes shake {
  0%, 100% {
    transform: translateX(0);
  }
  25% {
    transform: translateX(-5px);
  }
  75% {
    transform: translateX(5px);
  }
}

@media (max-width: 600px) {
  .activation-status {
    padding: 24px 16px;
    min-height: 350px;
  }

  .status-title {
    font-size: 1.5rem;
  }

  .status-subtitle {
    font-size: 0.9rem;
  }
}
</style>
