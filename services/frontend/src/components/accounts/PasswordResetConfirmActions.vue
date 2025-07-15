<template>
  <div class="password-reset-confirm-actions">
    <v-btn
        type="submit"
        color="primary"
        size="large"
        block
        :loading="loading"
        :disabled="disabled"
        class="mb-4 action-btn"
        @click="$emit('submit')"
    >
      <v-icon start>mdi-key-change</v-icon>
      Reset Password
    </v-btn>

    <v-divider class="mb-4"/>

    <div class="text-center">
      <v-btn
          color="primary"
          variant="text"
          class="action-btn me-2"
          @click="$emit('go-to-login')"
      >
        <v-icon start>mdi-arrow-left</v-icon>
        Back to Login
      </v-btn>

      <v-btn
          color="primary"
          variant="text"
          class="action-btn"
          @click="$emit('go-to-reset')"
      >
        <v-icon start>mdi-refresh</v-icon>
        Request New Link
      </v-btn>
    </div>
  </div>
</template>

<script setup>
defineProps({
  loading: {
    type: Boolean,
    default: false
  },
  disabled: {
    type: Boolean,
    default: false
  }
})

defineEmits(['submit', 'go-to-login', 'go-to-reset'])
</script>

<style scoped>
.password-reset-confirm-actions {
  width: 100%;
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
  .action-btn {
    font-size: 14px;
  }

  .action-btn.me-2 {
    margin-right: 4px !important;
    margin-bottom: 8px;
  }
}
</style>
