<template>
  <div class="d-flex justify-center align-center my-10">
    <v-progress-circular
        :color="props.color"
        indeterminate
        :size="props.size"
    ></v-progress-circular>
  </div>
</template>

<script setup>
const props = defineProps({
  color: {
    type: String,
    default: 'primary'
  },
  size: {
    type: Number,
    default: 64
  }
});
</script>
