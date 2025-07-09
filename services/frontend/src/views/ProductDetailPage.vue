<template>
  <div class="product-detail-page">
    <div class="container-custom mx-auto my-6">
      <!-- Breadcrumbs -->
      <product-breadcrumbs :items="breadcrumbItems"/>

      <!-- Loader -->
      <content-loader v-if="isLoading"/>

      <!-- Error message -->
      <error-alert
          v-if="error"
          :message="error.message"
      />

      <!-- Product Details -->
      <v-row
          v-if="hasProduct"
          :key="product.product_id"
      >
        <!-- Product Image -->
        <v-col cols="12" md="6">
          <product-image-card
              :product="product"
              :image-loading="imageLoading"
              @image-loaded="handleImageLoaded"
          />
        </v-col>

        <!-- Product Info -->
        <v-col cols="12" md="6">
          <product-info-card
              :product="product"
              @go-back="goBack"
          />
        </v-col>
      </v-row>

      <!-- Product not found -->
      <no-items-found
          v-if="showNotFound"
          title="Product not found"
          message="The product you're looking for doesn't exist or has been removed"
          icon="mdi-package-variant-remove"
      />
    </div>
  </div>
</template>

<script setup>
import {useProductDetail} from '@/composables/product/useProductDetail';

import ProductBreadcrumbs from '@/components/product/ProductBreadcrumbs.vue';
import ProductImageCard from '@/components/product/ProductImageCard.vue';
import ProductInfoCard from '@/components/product/ProductInfoCard.vue';
import ContentLoader from '@/components/ui/loaders/ContentLoader.vue';
import ErrorAlert from '@/components/ui/alerts/ErrorAlert.vue';
import NoItemsFound from '@/components/ui/empty-states/NoItemsFound.vue';

const props = defineProps({
  productSlug: {
    type: String,
    required: true
  },
  productId: {
    type: Number,
    default: null
  }
});

const {
  product,
  isLoading,
  error,
  hasProduct,
  showNotFound,
  imageLoading,
  breadcrumbItems,
  goBack,
  handleImageLoaded
} = useProductDetail(props);
</script>

<style scoped>
.product-detail-page {
  min-height: calc(100vh - 64px);
}

.container-custom {
  width: 100%;
  max-width: 1280px;
  padding: 0 16px;
  box-sizing: border-box;
}

@media (min-width: 960px) {
  .container-custom {
    padding: 0 24px;
  }
}

@media (min-width: 1440px) {
  .container-custom {
    max-width: 1400px;
  }
}

@media (max-width: 960px) {
  .product-info {
    margin-top: 24px;
  }
}
</style>
