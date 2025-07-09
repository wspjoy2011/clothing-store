<template>
  <div class="action-buttons-section">
    <v-divider class="my-4" />

    <v-btn
        v-if="needsActivation"
        variant="outlined"
        block
        size="large"
        color="warning"
        class="action-btn mb-2"
        :disabled="isLoading || isSocialAuthLoading"
        @click="$emit('activate')"
    >
      <v-icon start icon="mdi-email-check" />
      Activate Account
    </v-btn>

    <v-btn
        v-if="needsRegistration"
        variant="outlined"
        block
        size="large"
        color="success"
        class="action-btn"
        :disabled="isLoading || isSocialAuthLoading"
        @click="$emit('register')"
    >
      <v-icon start icon="mdi-account-plus" />
      Create Account
    </v-btn>
  </div>
</template>

<script setup>
defineProps({
  needsActivation: {
    type: Boolean,
    default: false
  },
  needsRegistration: {
    type: Boolean,
    default: false
  },
  isLoading: {
    type: Boolean,
    default: false
  },
  isSocialAuthLoading: {
    type: Boolean,
    default: false
  }
});

defineEmits(['activate', 'register']);
</script>

<style scoped>
.action-buttons-section {
  margin-top: 16px;
}

.action-btn {
  font-weight: 500;
  text-transform: none;
}
</style>
