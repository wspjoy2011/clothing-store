<template>
  <v-row>
    <v-col cols="12" class="text-center my-10">
      <v-icon :icon="props.icon" size="x-large" class="mb-4"></v-icon>
      <h3 class="text-h5">{{ props.title }}</h3>
      <p class="text-body-1 mt-2">{{ props.message }}</p>
    </v-col>
  </v-row>
</template>

<script setup>
const props = defineProps({
  title: {
    type: String,
    default: 'No items found'
  },
  message: {
    type: String,
    default: 'Sorry, there are no items in this category.'
  },
  icon: {
    type: String,
    default: 'mdi-alert-circle-outline'
  }
});
</script>
