<template>
  <div class="mobile-controls">
    <div class="quantity-controls">
      <v-btn
          icon
          size="x-small"
          variant="outlined"
          color="primary"
          :disabled="item.quantity <= 1 || updating"
          @click="$emit('decrease')"
      >
        <v-icon size="12">mdi-minus</v-icon>
      </v-btn>

      <span class="quantity-display">{{ item.quantity }}</span>

      <v-btn
          icon
          size="x-small"
          variant="outlined"
          color="primary"
          :disabled="!isAvailable || updating || (maxAvailable !== null && item.quantity >= maxAvailable)"
          @click="$emit('increase')"
          :title="maxAvailable !== null && item.quantity >= maxAvailable ? 'Maximum available reached' : ''"
      >
        <v-icon size="12">mdi-plus</v-icon>
      </v-btn>
    </div>

    <div class="item-actions">
      <v-btn
          icon
          size="small"
          variant="text"
          color="error"
          @click="$emit('remove')"
          :loading="removing"
      >
        <v-icon size="16">mdi-delete</v-icon>
      </v-btn>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  item: {type: Object, required: true},
  updating: {type: Boolean, default: false},
  removing: {type: Boolean, default: false},
  maxAvailable: {type: Number, default: null},
  isAvailable: {type: Boolean, default: true}
})
defineEmits(['increase', 'decrease', 'remove'])
</script>

<style scoped>
.mobile-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
}

.quantity-controls {
  display: flex;
  align-items: center;
  gap: 12px;
}

.quantity-display {
  min-width: 20px;
  text-align: center;
  font-weight: 600;
  font-size: 0.9rem;
  color: #1a1a1a;
}

/* Dark theme support */
:deep(.v-theme--dark) {
  .quantity-display {
    color: #e8eaed;
  }
}
</style>
