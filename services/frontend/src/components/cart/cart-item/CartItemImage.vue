<template>
  <div class="product-image-container">
    <v-img
        :src="item.product_image_url"
        :alt="item.product_name"
        height="80"
        width="80"
        cover
        class="product-image"
        @click="$emit('view-product')"
    >
      <template #placeholder>
        <div class="image-placeholder">
          <v-icon icon="mdi-image" size="24" color="grey-lighten-2"/>
        </div>
      </template>
    </v-img>

    <div v-if="!item.is_available" class="availability-badge">
      <v-chip color="error" size="x-small" variant="elevated">
        Out of Stock
      </v-chip>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  item: {type: Object, required: true}
})
defineEmits(['view-product'])
</script>

<style scoped>
.product-image-container {
  position: relative;
  cursor: pointer;
  border-radius: 8px;
  overflow: hidden;
}

.product-image {
  border-radius: 8px;
  transition: transform 0.2s ease;
}

.product-image:hover {
  transform: scale(1.05);
}

.image-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  background-color: #f5f5f5;
}

.availability-badge {
  position: absolute;
  top: -4px;
  right: -4px;
  z-index: 1;
}

/* Dark theme support */
:deep(.v-theme--dark) {
  .image-placeholder {
    background-color: rgba(255, 255, 255, 0.05);
  }
}
</style>
