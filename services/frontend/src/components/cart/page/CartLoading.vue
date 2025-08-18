<template>
  <div class="loading-section">
    <v-row justify="center" class="py-12">
      <v-col cols="12" class="text-center">
        <v-progress-circular
            color="primary"
            indeterminate
            size="64"
            width="4"
            class="mb-4"
        />
        <h3 class="text-h6 text-medium-emphasis">Loading your cart...</h3>
      </v-col>
    </v-row>
  </div>
</template>

<script setup>
</script>

<style scoped>
.loading-section {
  background: rgba(255, 255, 255, 0.9);
  border-radius: 16px;
  backdrop-filter: blur(10px);
}

:deep(.dark-theme) .loading-section {
  background: rgba(48, 48, 48, 0.9);
}
</style>
