<template>
  <div class="item-total">
    <div class="total-price">
      <div v-if="hasDiscount" class="sale-total">
        ${{ saleTotal }}
      </div>
      <div v-else class="regular-total">
        ${{ regularTotal }}
      </div>
    </div>

    <v-btn
        icon
        size="small"
        variant="text"
        color="error"
        @click="$emit('remove')"
        :loading="removing"
        class="remove-btn"
    >
      <v-icon size="18">mdi-delete</v-icon>
    </v-btn>
  </div>
</template>

<script setup>
const props = defineProps({
  hasDiscount: {type: Boolean, default: false},
  saleTotal: {type: [String, Number], default: ''},
  regularTotal: {type: [String, Number], default: ''},
  removing: {type: Boolean, default: false}
})
defineEmits(['remove'])
</script>

<style scoped>
.item-total {
  text-align: center;
}

.total-price {
  margin-bottom: 8px;
}

.sale-total,
.regular-total {
  font-size: 1.1rem;
  font-weight: 700;
  color: #1976d2;
}

.sale-total {
  color: #d32f2f;
}

.remove-btn {
  transition: all 0.2s ease;
}

.remove-btn:hover {
  background-color: rgba(244, 67, 54, 0.1);
}

/* Dark theme support */
:deep(.v-theme--dark) {
  .sale-total {
    color: #ff6b6b;
  }

  .regular-total {
    color: #90caf9;
  }
}
</style>
