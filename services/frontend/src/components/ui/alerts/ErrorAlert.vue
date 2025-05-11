<template>
  <v-alert
      type="error"
      variant="tonal"
      class="mb-6"
  >
    {{ props.message }}
  </v-alert>
</template>

<script setup>
const props = defineProps({
  message: {
    type: String,
    required: true
  }
});
</script>
