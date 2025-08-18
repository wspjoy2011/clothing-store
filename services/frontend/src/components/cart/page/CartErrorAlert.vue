<template>
  <v-alert
      type="error"
      variant="tonal"
      class="mb-6"
      closable
      @click:close="$emit('clear')"
  >
    <template #title>
      <span class="text-subtitle-1 font-weight-bold">Cart Error</span>
    </template>
    <div class="error-content">
      <p class="mb-2">{{ message }}</p>
      <div class="error-actions">
        <v-btn
            size="small"
            variant="outlined"
            color="error"
            @click="$emit('retry')"
            :loading="isLoading"
            class="me-2"
        >
          Retry
        </v-btn>
      </div>
    </div>
  </v-alert>
</template>

<script setup>
const props = defineProps({
  message: {type: String, default: ''},
  isLoading: {type: Boolean, default: false}
})
defineEmits(['retry', 'clear'])
</script>

<style scoped>
.error-content {
  margin-top: 8px;
}

.error-actions {
  margin-top: 16px;
}
</style>
