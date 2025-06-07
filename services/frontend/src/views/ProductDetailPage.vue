<template>
  <div class="product-detail-page">
    <div class="container-custom mx-auto my-6">
      <v-row justify="center">
        <v-col cols="12">
          <v-breadcrumbs
              :items="breadcrumbItems"
              density="compact"
              class="px-0"
          >
            <template v-slot:divider>
              <v-icon icon="mdi-chevron-right" size="small"/>
            </template>
          </v-breadcrumbs>
        </v-col>
      </v-row>

      <!-- Loader -->
      <content-loader v-if="catalogStore.productLoading"/>

      <!-- Error message -->
      <error-alert
          v-if="catalogStore.productError"
          :message="catalogStore.productError.message"
      />

      <!-- Product Details -->
      <v-row v-if="!catalogStore.productLoading && !catalogStore.productError && catalogStore.currentProduct">
        <!-- Product Image -->
        <v-col cols="12" md="6">
          <v-card class="product-image-card" elevation="2">
            <div class="position-relative">
              <div v-if="imageLoading" class="image-loader">
                <v-progress-circular color="primary" indeterminate size="40"/>
              </div>
              <v-img
                  :src="catalogStore.currentProduct.image_url"
                  :alt="catalogStore.currentProduct.product_display_name"
                  height="500"
                  cover
                  class="product-detail-image"
                  @load="imageLoaded"
                  @error="imageLoaded"
              />
            </div>
          </v-card>
        </v-col>

        <!-- Product Info -->
        <v-col cols="12" md="6">
          <div class="product-info">
            <!-- Product Title -->
            <h1 class="text-h4 font-weight-bold mb-4">
              {{ catalogStore.currentProduct.product_display_name }}
            </h1>

            <!-- Product Meta -->
            <v-sheet rounded class="pa-4 mb-4 product-meta-sheet" color="grey-lighten-5">
              <div class="product-meta">
                <div class="meta-item">
                  <v-icon icon="mdi-account" class="mr-2" color="primary"/>
                  <span class="meta-label">Gender:</span>
                  <v-chip
                      color="primary"
                      variant="outlined"
                      size="small"
                      class="ml-2"
                  >
                    {{ catalogStore.currentProduct.gender }}
                  </v-chip>
                </div>

                <div class="meta-item mt-3">
                  <v-icon icon="mdi-calendar" class="mr-2" color="primary"/>
                  <span class="meta-label">Year:</span>
                  <v-chip
                      color="secondary"
                      variant="outlined"
                      size="small"
                      class="ml-2"
                  >
                    {{ catalogStore.currentProduct.year }}
                  </v-chip>
                </div>

                <div class="meta-item mt-3">
                  <v-icon icon="mdi-identifier" class="mr-2" color="primary"/>
                  <span class="meta-label">Product ID:</span>
                  <span class="ml-2 font-weight-medium product-id-text">
                    #{{ catalogStore.currentProduct.product_id }}
                  </span>
                </div>
              </div>
            </v-sheet>

            <!-- Action Buttons -->
            <div class="action-buttons">
              <v-btn
                  color="primary"
                  size="large"
                  variant="flat"
                  block
                  class="mb-3"
                  prepend-icon="mdi-cart-plus"
              >
                Add to Cart
              </v-btn>

              <v-btn
                  color="secondary"
                  size="large"
                  variant="outlined"
                  block
                  class="mb-3"
                  prepend-icon="mdi-heart-outline"
              >
                Add to Wishlist
              </v-btn>

              <v-btn
                  color="primary"
                  variant="text"
                  block
                  @click="goBack"
                  prepend-icon="mdi-arrow-left"
              >
                Back to Catalog
              </v-btn>
            </div>
          </div>
        </v-col>
      </v-row>

      <!-- Product not found -->
      <no-items-found
          v-if="!catalogStore.productLoading && !catalogStore.productError && !catalogStore.currentProduct"
          title="Product not found"
          message="The product you're looking for doesn't exist or has been removed"
          icon="mdi-package-variant-remove"
      />
    </div>
  </div>
</template>

<script setup>
import {ref, computed, onMounted, onUnmounted, watch} from 'vue';
import {useRoute, useRouter} from 'vue-router';
import {useCatalogStore} from '@/stores/catalog';

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

const route = useRoute();
const router = useRouter();
const catalogStore = useCatalogStore();

const imageLoading = ref(true);

const breadcrumbItems = computed(() => [
  {
    title: 'Home',
    disabled: false,
    to: {name: 'home'}
  },
  {
    title: 'Catalog',
    disabled: false,
    to: {name: 'catalog'}
  },
  {
    title: catalogStore.currentProduct?.product_display_name || 'Product',
    disabled: true
  }
]);

const imageLoaded = () => {
  imageLoading.value = false;
};

const goBack = () => {
  if (window.history.length > 1) {
    router.go(-1);
  } else {
    router.push({name: 'catalog'});
  }
};

const loadProduct = async () => {
  try {
    if (props.productId) {
      await catalogStore.getProductById(props.productId);
      if (catalogStore.currentProduct) {
        document.title = `StyleShop - ${catalogStore.currentProduct.product_display_name}`;
      }
      return;
    }

    const existingProductId = catalogStore.getProductIdBySlug(props.productSlug);
    if (existingProductId) {
      await catalogStore.getProductById(existingProductId);
      if (catalogStore.currentProduct) {
        document.title = `StyleShop - ${catalogStore.currentProduct.product_display_name}`;
      }
      return;
    }

    await catalogStore.getProductBySlug(props.productSlug);
    if (catalogStore.currentProduct) {
      document.title = `StyleShop - ${catalogStore.currentProduct.product_display_name}`;
    }

  } catch (error) {
    console.error('Error loading product:', error);
  }
};

watch(() => props.productId, (newId) => {
  if (newId) {
    loadProduct();
  }
}, {immediate: false});

watch(() => props.productSlug, (newSlug) => {
  if (newSlug && !props.productId) {
    loadProduct();
  }
}, {immediate: false});

onMounted(() => {
  catalogStore.clearCurrentProduct();
  loadProduct();
});

onUnmounted(() => {
  catalogStore.clearCurrentProduct();
});
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

.product-info {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.product-meta {
  display: flex;
  flex-direction: column;
}

.meta-item {
  display: flex;
  align-items: center;
}

.meta-label {
  font-weight: 500;
  color: #424242;
}

.product-id-text {
  color: #424242;
}

.action-buttons {
  margin-top: auto;
}

.v-theme--dark .product-meta-sheet {
  background-color: #2c2c2c !important;
}

.v-theme--dark .meta-label {
  color: #ffffff !important;
}

.v-theme--dark .product-id-text {
  color: #ffffff !important;
}

@media (min-width: 960px) {
  .container-custom {
    padding: 0 24px;
  }

  .product-info {
    padding-left: 24px;
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
