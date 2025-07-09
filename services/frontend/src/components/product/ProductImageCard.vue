<template>
  <v-card class="product-image-card" elevation="2">
    <div class="position-relative">
      <div v-if="imageLoading" class="image-loader">
        <v-progress-circular color="primary" indeterminate size="40"/>
      </div>
      <v-img
          :src="product.image_url"
          :alt="product.product_display_name"
          height="500"
          cover
          class="product-detail-image"
          @load="handleImageLoaded"
          @error="handleImageLoaded"
      />
    </div>
  </v-card>
</template>

<script setup>
const props = defineProps({
  product: {
    type: Object,
    required: true
  },
  imageLoading: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['image-loaded']);

const handleImageLoaded = () => {
  emit('image-loaded');
};
</script>

<style scoped>
.product-image-card {
  overflow: hidden;
}

.position-relative {
  position: relative;
  height: 500px;
}

.image-loader {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: rgba(245, 245, 245, 0.7);
  z-index: 1;
}

.product-detail-image {
  transition: transform 0.3s ease;
}

.product-detail-image:hover {
  transform: scale(1.05);
}
</style>
