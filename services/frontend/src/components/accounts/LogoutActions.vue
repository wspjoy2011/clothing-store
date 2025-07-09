<template>
  <v-card-actions class="logout-actions">
    <div class="action-buttons">
      <v-btn
          color="primary"
          variant="elevated"
          block
          size="large"
          @click="$emit('go-home')"
          :disabled="isLoading"
      >
        <v-icon start icon="mdi-home"></v-icon>
        Go to Home
      </v-btn>

      <div class="secondary-actions mt-3">
        <v-btn
            variant="outlined"
            color="primary"
            block
            @click="$emit('go-login')"
            :disabled="isLoading"
        >
          <v-icon start icon="mdi-login"></v-icon>
          Sign In Again
        </v-btn>
      </div>
    </div>
  </v-card-actions>
</template>

<script setup>
defineProps({
  isLoading: {
    type: Boolean,
    default: false
  }
});

defineEmits(['go-home', 'go-login']);
</script>

<style scoped>
.logout-actions {
  padding: 1rem 2rem 2rem;
}

.action-buttons {
  width: 100%;
}

.secondary-actions {
  display: flex;
  gap: 0.5rem;
}

.secondary-actions .v-btn {
  flex: 1;
}

@media (max-width: 600px) {
  .logout-actions {
    padding: 1rem 1.5rem 1.5rem;
  }

  .secondary-actions {
    flex-direction: column;
    gap: 0.75rem;
  }

  .secondary-actions .v-btn {
    flex: none;
  }
}
</style>
