<template>
  <div class="password-reset-confirm-status-card">
    <v-alert
        :type="success ? 'success' : 'error'"
        variant="tonal"
        class="mb-6"
        :icon="success ? 'mdi-check-circle' : 'mdi-alert-circle'"
    >
      <div class="text-subtitle-1 font-weight-medium">
        {{ success ? 'Password Reset Successful!' : 'Password Reset Failed' }}
      </div>
      <div class="text-body-2 mt-1">
        {{ message }}
      </div>
    </v-alert>

    <div v-if="showActions && success" class="text-center">
      <v-btn
          color="primary"
          size="large"
          class="action-btn mb-3"
          @click="$emit('go-to-login')"
      >
        <v-icon start>mdi-login</v-icon>
        Login Now
      </v-btn>

      <div class="text-body-2 text-medium-emphasis">
        You will be redirected to login in {{ countdown }} seconds...
      </div>
    </div>

    <div v-if="showActions && !success" class="text-center">
      <v-btn
          color="primary"
          variant="outlined"
          size="large"
          class="action-btn mb-2"
          @click="$emit('try-again')"
      >
        <v-icon start>mdi-refresh</v-icon>
        Try Again
      </v-btn>

      <v-btn
          color="primary"
          variant="text"
          class="action-btn"
          @click="$emit('request-new-link')"
      >
        <v-icon start>mdi-email</v-icon>
        Request New Link
      </v-btn>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  success: {
    type: Boolean,
    default: false
  },
  message: {
    type: String,
    default: ''
  },
  showActions: {
    type: Boolean,
    default: true
  },
  redirectDelay: {
    type: Number,
    default: 3
  }
})

const emit = defineEmits(['go-to-login', 'try-again', 'request-new-link'])

const countdown = ref(props.redirectDelay)
let countdownInterval = null

onMounted(() => {
  if (props.success && props.showActions) {
    countdownInterval = setInterval(() => {
      countdown.value--
      if (countdown.value <= 0) {
        emit('go-to-login')
        clearInterval(countdownInterval)
      }
    }, 1000)
  }
})

onUnmounted(() => {
  if (countdownInterval) {
    clearInterval(countdownInterval)
  }
})
</script>

<style scoped>
.password-reset-confirm-status-card {
  width: 100%;
}

.action-btn {
  border-radius: 12px;
  font-weight: 600;
  text-transform: none;
  letter-spacing: 0.025em;
  transition: all 0.3s ease;
  margin-bottom: 8px;
}

.action-btn:hover {
  transform: translateY(-2px);
}

@media (max-width: 600px) {
  .action-btn {
    font-size: 14px;
    width: 100%;
  }
}
</style>
