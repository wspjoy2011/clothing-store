<template>
  <v-card
      class="mx-auto my-3 product-card"
      :elevation="hover ? 8 : 2"
      @mouseenter="hover = true"
      @mouseleave="hover = false"
  >
    <div class="position-relative">
      <div v-if="imageLoading" class="image-loader">
        <v-progress-circular color="primary" indeterminate size="30"/>
      </div>
      <v-img
          :src="props.product.image_url"
          height="250"
          cover
          class="product-image"
          @load="imageLoaded"
          @error="imageLoaded"
      />
    </div>

    <v-card-title class="text-subtitle-1 font-weight-bold d-block text-truncate">
      {{ props.product.product_display_name }}
    </v-card-title>

    <v-card-subtitle>
      <span class="font-weight-medium">{{ props.product.gender }}</span>
      <span class="ms-2 text-medium-emphasis text-caption">{{ props.product.year }}</span>
    </v-card-subtitle>

    <v-card-actions>
      <v-btn
          color="primary"
          variant="flat"
          class="text-none"
          block
          @click="goToProductDetail"
      >
        View Details
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script setup>
import {ref} from 'vue';
import {useRouter} from 'vue-router';

const props = defineProps({
  product: {
    type: Object,
    required: true,
    validator: (product) => {
      return [
        'product_id',
        'gender',
        'year',
        'product_display_name',
        'image_url',
        'slug'
      ].every(prop => prop in product);
    }
  }
});

const router = useRouter();
const hover = ref(false);
const imageLoading = ref(true);

const imageLoaded = () => {
  imageLoading.value = false;
};

const goToProductDetail = () => {
  router.push({
    name: 'product-detail',
    params: {
      productSlug: props.product.slug
    }
  });
};
</script>

<style scoped>
.product-card {
  transition: transform 0.2s ease-in-out;
  width: 100%;
  cursor: pointer;
}

.product-card:hover {
  transform: translateY(-5px);
}

.product-image {
  transition: opacity 0.3s;
}

.product-image:hover {
  opacity: 0.85;
}

.position-relative {
  position: relative;
  height: 250px;
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
</style>
