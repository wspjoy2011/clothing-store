<template>
  <div class="d-flex align-center">
    <v-icon icon="mdi-store" size="large" class="mr-2"></v-icon>
    <span class="text-h5 font-weight-bold cursor-pointer" @click="$emit('go-to-home')">
      StyleShop
    </span>

    <v-btn
        v-if="showCategoryPath"
        variant="text"
        class="ml-3 category-path-indicator hidden-md-and-down"
        @click="$emit('toggle-category-path')"
    >
      <v-icon icon="mdi-tag-multiple" class="mr-1" size="small"></v-icon>
      <span class="text-subtitle-2">{{ shortCategoryPathText }}</span>
      <v-icon :icon="categoryPathVisible ? 'mdi-chevron-up' : 'mdi-chevron-down'" class="ml-1" size="small"></v-icon>
    </v-btn>
  </div>
</template>

<script setup>
defineProps({
  showCategoryPath: {
    type: Boolean,
    default: false
  },
  categoryPathVisible: {
    type: Boolean,
    default: false
  },
  shortCategoryPathText: {
    type: String,
    default: ''
  }
})

defineEmits(['go-to-home', 'toggle-category-path'])
</script>

<style scoped>
.cursor-pointer {
  cursor: pointer;
}

.category-path-indicator {
  display: flex;
  align-items: center;
  border-radius: 20px;
  padding: 0 12px;
  height: 32px;
  background-color: rgba(0, 0, 0, 0.05);
  transition: background-color 0.2s ease;
}

.category-path-indicator:hover {
  background-color: rgba(0, 0, 0, 0.1);
}

:deep(.v-theme--dark) .category-path-indicator {
  background-color: rgba(255, 255, 255, 0.1);
}

:deep(.v-theme--dark) .category-path-indicator:hover {
  background-color: rgba(255, 255, 255, 0.15);
}
</style>
