<template>
  <div class="quantity-row">
    <span class="text-caption text-medium-emphasis">Quantity:</span>
    <div class="quantity-controls">
      <v-btn
        icon
        size="x-small"
        variant="outlined"
        color="primary"
        :disabled="quantity <= 1"
        @click="decrease"
      >
        <v-icon size="14">mdi-minus</v-icon>
      </v-btn>
      <span class="quantity-display">{{ quantity }}</span>
      <v-btn
        icon
        size="x-small"
        variant="outlined"
        color="primary"
        :disabled="quantity >= availableQuantity"
        @click="increase"
      >
        <v-icon size="14">mdi-plus</v-icon>
      </v-btn>
    </div>
  </div>
</template>
<script setup>
const props = defineProps({
  quantity: Number,
  availableQuantity: Number,
  decrease: Function,
  increase: Function,
});
</script>
<style scoped>
.quantity-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}
.quantity-controls {
  display: flex;
  align-items: center;
  gap: 12px;
}
.quantity-display {
  min-width: 20px;
  text-align: center;
  font-weight: bold;
}
</style>
