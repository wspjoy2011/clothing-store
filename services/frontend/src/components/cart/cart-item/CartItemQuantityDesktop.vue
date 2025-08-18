<template>
  <div class="quantity-controls-desktop">
    <v-btn
        icon
        size="small"
        variant="outlined"
        color="primary"
        :disabled="item.quantity <= 1 || updating"
        @click="$emit('decrease')"
    >
      <v-icon size="14">mdi-minus</v-icon>
    </v-btn>

    <span class="quantity-display-desktop">{{ item.quantity }}</span>

    <v-btn
        icon
        size="small"
        variant="outlined"
        color="primary"
        :disabled="!isAvailable || updating || (maxAvailable !== null && item.quantity >= maxAvailable)"
        @click="$emit('increase')"
        :title="maxAvailable !== null && item.quantity >= maxAvailable ? 'Maximum available reached' : ''"
    >
      <v-icon size="14">mdi-plus</v-icon>
    </v-btn>
  </div>
</template>

<script setup>
const props = defineProps({
  item: {type: Object, required: true},
  updating: {type: Boolean, default: false},
  maxAvailable: {type: Number, default: null},
  isAvailable: {type: Boolean, default: true}
})
defineEmits(['increase', 'decrease'])
</script>

<style scoped>
.quantity-controls-desktop {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.quantity-display-desktop {
  min-width: 24px;
  text-align: center;
  font-weight: 600;
  font-size: 1rem;
  color: #1a1a1a;
}

/* Dark theme support */
:deep(.v-theme--dark) {
  .quantity-display-desktop {
    color: #e8eaed;
  }
}
</style>
