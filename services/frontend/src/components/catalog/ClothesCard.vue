<template>
  <v-card class="mx-auto my-3 product-card" max-width="300" :elevation="hover ? 8 : 2" @mouseenter="hover = true"
          @mouseleave="hover = false">
    <v-img
        :src="product.image_url"
        height="250"
        cover
        class="product-image"
    />

    <v-card-title class="text-subtitle-1 font-weight-bold d-block text-truncate">
      {{ product.product_display_name }}
    </v-card-title>

    <v-card-subtitle>
      <span class="font-weight-medium">{{ product.gender }}</span>
      <span class="ms-2 text-medium-emphasis text-caption">{{ product.year }}</span>
    </v-card-subtitle>

    <v-card-actions>
      <v-btn
          color="primary"
          variant="flat"
          class="text-none"
          block
      >
        View Details
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script setup>
import {ref} from 'vue';

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
        'image_url'
      ].every(prop => prop in product);
    }
  }
});

const hover = ref(false);
</script>

<style scoped>
.product-card {
  transition: transform 0.2s ease-in-out;
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
</style>