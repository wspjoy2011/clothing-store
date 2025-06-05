<template>
  <div class="catalog-layout">
    <!-- Filter Drawer -->
    <v-navigation-drawer
        v-model="categoryStore.isFilterDrawerOpen"
        location="left"
        temporary
        width="320"
        class="filter-drawer"
    >
      <div class="drawer-header">
        <h3 class="text-h6">Filters</h3>
        <v-btn icon="mdi-close" variant="text" size="small" @click="categoryStore.toggleFilterDrawer(false)"/>
      </div>
      <filter-sidebar/>
    </v-navigation-drawer>

    <!-- Filter Toggle Button -->
    <div v-if="hasProducts" class="filter-toggle-container">
      <v-btn
          icon="mdi-filter"
          variant="outlined"
          size="small"
          class="filter-btn"
          @click="categoryStore.toggleFilterDrawer(true)"
      >
        <v-badge
            :content="categoryStore.activeFiltersCount"
            :value="categoryStore.activeFiltersCount > 0"
            :color="categoryStore.activeFiltersCount > 0 ? 'error' : 'primary'"
            location="top end"
        />
      </v-btn>
    </div>

    <!-- Main Content Area -->
    <div class="main-content">
      <div class="container-custom mx-auto my-6">
        <!-- Breadcrumbs -->
        <div class="breadcrumbs-container mb-5">
          <nav aria-label="breadcrumb">
            <ul class="breadcrumbs">
              <li class="breadcrumb-item">
                <router-link to="/" class="breadcrumb-link">
                  <v-icon icon="mdi-home" size="small" class="breadcrumb-icon"/>
                  <span>Home</span>
                </router-link>
              </li>

              <li class="breadcrumb-divider">
                <v-icon icon="mdi-chevron-right" size="small" class="chevron-icon"/>
              </li>

              <li class="breadcrumb-item">
                <router-link to="/catalog" class="breadcrumb-link">
                  <v-icon icon="mdi-shopping" size="small" class="breadcrumb-icon"/>
                  <span>Catalog</span>
                </router-link>
              </li>

              <template v-if="masterCategory">
                <li class="breadcrumb-divider">
                  <v-icon icon="mdi-chevron-right" size="small" class="chevron-icon"/>
                </li>
                <li class="breadcrumb-item" :class="{ 'active': route.name === 'master-category' }">
                  <router-link
                      v-if="route.name !== 'master-category'"
                      :to="{ name: 'master-category', params: { masterCategory: masterCategorySlug } }"
                      class="breadcrumb-link"
                  >
                    <v-icon icon="mdi-shape" size="small" class="breadcrumb-icon"/>
                    <span>{{ masterCategory.name }}</span>
                  </router-link>
                  <span v-else class="breadcrumb-text">
                    <v-icon icon="mdi-shape" size="small" class="breadcrumb-icon"/>
                    {{ masterCategory.name }}
                  </span>
                </li>
              </template>

              <template v-if="subCategory">
                <li class="breadcrumb-divider">
                  <v-icon icon="mdi-chevron-right" size="small" class="chevron-icon"/>
                </li>
                <li class="breadcrumb-item" :class="{ 'active': route.name === 'sub-category' }">
                  <router-link
                      v-if="subCategorySlug && route.name !== 'sub-category'"
                      :to="{ name: 'sub-category', params: { masterCategory: masterCategorySlug, subCategory: subCategorySlug } }"
                      class="breadcrumb-link"
                  >
                    <v-icon icon="mdi-tag" size="small" class="breadcrumb-icon"/>
                    <span>{{ subCategory.name }}</span>
                  </router-link>
                  <span v-else class="breadcrumb-text">
                    <v-icon icon="mdi-tag" size="small" class="breadcrumb-icon"/>
                    {{ subCategory.name }}
                  </span>
                </li>
              </template>

              <template v-if="articleType">
                <li class="breadcrumb-divider">
                  <v-icon icon="mdi-chevron-right" size="small" class="chevron-icon"/>
                </li>
                <li class="breadcrumb-item active">
                  <span class="breadcrumb-text">
                    <v-icon icon="mdi-tshirt-crew" size="small" class="breadcrumb-icon"/>
                    {{ articleType.name }}
                  </span>
                </li>
              </template>
            </ul>
          </nav>
        </div>

        <!-- Category Header -->
        <div class="category-header mb-6 text-center">
          <h1 class="text-h4 font-weight-bold mb-3">
            {{ currentCategoryTitle }}
          </h1>
          <div class="divider-container">
            <div class="divider-line"></div>
          </div>
          <p class="text-subtitle-1 mt-4 mx-auto" v-if="currentCategoryDescription" style="max-width: 800px;">
            {{ currentCategoryDescription }}
          </p>
        </div>

        <!-- Search results indicator -->
        <v-row v-if="searchQuery && searchQuery.trim()" justify="center" class="mb-6">
          <v-col cols="12" class="text-center">
            <v-chip
                color="primary"
                variant="outlined"
                size="large"
                closable
                @click:close="clearSearch"
                prepend-icon="mdi-magnify"
            >
              Search results for: "{{ searchQuery }}"
            </v-chip>
          </v-col>
        </v-row>

        <!-- Control panel -->
        <v-row v-if="hasProducts" justify="center" align="center" class="mb-3">
          <v-col cols="12" sm="6" md="4" lg="3">
            <product-sorting @update:ordering="handleOrderingChange"/>
          </v-col>

          <v-spacer class="d-none d-md-flex"></v-spacer>

          <v-col cols="12" sm="6" md="4" lg="3" class="d-flex justify-end">
            <items-per-page-select
                :options="itemsPerPageOptions"
                @update:perPage="handleItemsPerPageChange"
            />
          </v-col>
        </v-row>

        <!-- Active filters summary -->
        <v-row v-if="categoryStore.hasActiveFilters && !isLoading" class="mb-4">
          <v-col cols="12">
            <v-sheet rounded class="pa-3" color="grey-lighten-4">
              <div class="d-flex align-center justify-space-between">
                <div class="d-flex align-center">
                  <v-icon icon="mdi-filter-variant" class="mr-2"/>
                  <span class="text-body-1">Active Filters</span>
                  <v-chip
                      v-if="activeFilters.gender"
                      size="small"
                      class="ml-2"
                      closable
                      @click:close="activeFilters.gender = null"
                  >
                    Gender: {{ activeFilters.gender }}
                  </v-chip>
                  <v-chip
                      v-if="activeFilters.min_year || activeFilters.max_year"
                      size="small"
                      class="ml-2"
                      closable
                      @click:close="activeFilters.min_year = null; activeFilters.max_year = null"
                  >
                    Year: {{
                      activeFilters.min_year || availableFilters.year?.min
                    }}-{{ activeFilters.max_year || availableFilters.year?.max }}
                  </v-chip>
                  <v-progress-circular
                      v-if="isLoadingFilters"
                      size="16"
                      width="2"
                      indeterminate
                      class="ml-2"
                      color="primary"
                  />
                </div>
                <v-btn
                    variant="text"
                    color="primary"
                    density="comfortable"
                    @click="clearAllFilters"
                    :disabled="isLoadingFilters"
                >
                  Clear All
                </v-btn>
              </div>
            </v-sheet>
          </v-col>
        </v-row>

        <!-- Filter loading error -->
        <v-row v-if="filtersError && !isLoadingFilters" class="mb-4">
          <v-col cols="12">
            <v-alert
                type="warning"
                variant="tonal"
                closable
                @click:close="filtersError = null"
            >
              <template v-slot:title>
                <span class="text-subtitle-1 font-weight-medium">Filter Loading Error</span>
              </template>
              <span class="text-body-2">
                Unable to load filters for this category. Some filtering options may not be available.
              </span>
            </v-alert>
          </v-col>
        </v-row>

        <!-- Loader -->
        <content-loader v-if="isLoading"/>

        <!-- Error message -->
        <error-alert v-if="error" :message="error.message"/>

        <!-- Products grid -->
        <v-row v-if="!isLoading && !error && products.length > 0">
          <v-col
              v-for="product in products"
              :key="product.product_id"
              cols="12"
              sm="6"
              md="4"
              lg="3"
          >
            <clothes-card :product="product"/>
          </v-col>
        </v-row>

        <!-- Products count indicator -->
        <v-row v-if="hasProducts" justify="center" class="mt-4 mb-4">
          <v-col cols="12" class="text-center">
            <v-chip
                color="primary"
                variant="flat"
                class="px-4 py-2"
                size="large"
            >
              <v-icon start icon="mdi-tag-multiple" class="mr-1"/>
              {{ totalItems }} products found in {{ currentCategoryTitle }}
            </v-chip>
          </v-col>
        </v-row>

        <!-- No products found -->
        <no-items-found
            v-if="isEmpty"
            title="No products found in this category"
            message="Try adjusting your filters or search query"
            icon="mdi-search-off"
        />

        <!-- Pagination -->
        <v-row justify="center" v-if="hasItems">
          <v-col cols="12" class="px-0">
            <app-pagination
                :current-page="currentPage"
                :total-pages="totalPages"
                @update:page="handlePageChange"
            />
          </v-col>
        </v-row>
      </div>
    </div>
  </div>
</template>

<script setup>
import {computed, onMounted, onUnmounted, provide, watch} from 'vue';
import {useRoute} from 'vue-router';
import {useCategoryStore} from '@/stores/categoryStore';
import {useCategoryProducts} from '@/composables/catalog/useCategoryProducts';

import ClothesCard from '@/components/catalog/ClothesCard.vue';
import ContentLoader from '@/components/ui/loaders/ContentLoader.vue';
import ErrorAlert from '@/components/ui/alerts/ErrorAlert.vue';
import AppPagination from '@/components/ui/pagination/AppPagination.vue';
import ItemsPerPageSelect from '@/components/ui/pagination/ItemsPerPageSelect.vue';
import NoItemsFound from '@/components/ui/empty-states/NoItemsFound.vue';
import ProductSorting from '@/components/ui/sorting/ProductSorting.vue';
import FilterSidebar from '@/components/ui/filters/FilterSidebar.vue';

const route = useRoute();
const categoryStore = useCategoryStore();

const masterCategorySlug = computed(() => route.params.masterCategory);
const subCategorySlug = computed(() => route.params.subCategory);
const articleTypeSlug = computed(() => route.params.articleType);

const masterCategoryId = computed(() => {
  return masterCategorySlug.value ?
      categoryStore.getMasterCategoryIdBySlug(masterCategorySlug.value) : null;
});

const subCategoryId = computed(() => {
  if (!masterCategoryId.value || !subCategorySlug.value) return null;
  return categoryStore.getSubCategoryIdBySlug(masterCategoryId.value, subCategorySlug.value);
});

const articleTypeId = computed(() => {
  if (!masterCategoryId.value || !subCategoryId.value || !articleTypeSlug.value) return null;
  return categoryStore.getArticleTypeIdBySlug(masterCategoryId.value, subCategoryId.value, articleTypeSlug.value);
});

const masterCategory = computed(() => {
  return masterCategoryId.value ?
      categoryStore.getMasterCategory(masterCategoryId.value) : null;
});

const subCategory = computed(() => {
  if (!masterCategoryId.value || !subCategoryId.value) return null;
  return categoryStore.getSubCategory(masterCategoryId.value, subCategoryId.value);
});

const articleType = computed(() => {
  if (!masterCategoryId.value || !subCategoryId.value || !articleTypeId.value) return null;
  return categoryStore.getArticleType(masterCategoryId.value, subCategoryId.value, articleTypeId.value);
});

const currentCategoryTitle = computed(() => {
  return categoryStore.getCategoryName(
      masterCategoryId.value,
      subCategoryId.value,
      articleTypeId.value
  );
});

const currentCategoryDescription = computed(() => {
  return categoryStore.getCategoryDescription(
      masterCategoryId.value,
      subCategoryId.value,
      articleTypeId.value
  );
});

const {
  isLoading,
  error,
  products,
  totalPages,
  totalItems,
  currentPage,

  isLoadingFilters,
  filtersError,
  availableFilters,
  activeFilters,
  searchQuery,

  hasProducts,
  isEmpty,
  hasItems,
  itemsPerPageOptions,

  handlePageChange,
  handleItemsPerPageChange,
  handleOrderingChange,
  clearSearch,
  clearAllFilters,

  initialize,
  cleanup,
  disableFilterWatcher,
  enableFilterWatcher,
} = useCategoryProducts(route);

provide('categoryAvailableFilters', availableFilters);
provide('filtersError', filtersError);
provide('hasActiveFilters', computed(() => categoryStore.hasActiveFilters));
provide('clearAllFilters', clearAllFilters);

watch(
  () => [route.params.masterCategory, route.params.subCategory, route.params.articleType],
  async (newParams, oldParams) => {
    if (newParams.some((param, index) => param !== oldParams?.[index])) {
      console.log('Category route changed, reinitializing...');

      disableFilterWatcher();

      categoryStore.resetCategoryFilters();

      if (!categoryStore.hasCategories) {
        await categoryStore.fetchCategoryMenu();
      }

      await initialize();

      enableFilterWatcher();
    }
  },
  { immediate: false }
);

const cleanupComponent = () => {
  if (categoryStore.isFilterDrawerOpen) {
    categoryStore.toggleFilterDrawer(false);
  }
  cleanup();
};

onMounted(async () => {
  if (!categoryStore.hasCategories) {
    await categoryStore.fetchCategoryMenu();
  }
  await initialize();
});

onUnmounted(() => {
  cleanupComponent();
});
</script>

<style scoped>
.catalog-layout {
  display: flex;
  min-height: calc(100vh - 64px);
  position: relative;
}

.filter-drawer {
  box-shadow: 0 0 15px rgba(0, 0, 0, 0.1);
}

.drawer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.filter-toggle-container {
  position: fixed;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  z-index: 5;
}

.filter-btn {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  background-color: white;
}

.main-content {
  flex-grow: 1;
  width: 100%;
  display: flex;
  justify-content: center;
}

.container-custom {
  width: 100%;
  max-width: 1280px;
  padding: 0 16px;
  box-sizing: border-box;
}

.category-header {
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  padding-bottom: 16px;
}

.divider-container {
  display: flex;
  justify-content: center;
  margin-top: 16px;
}

.divider-line {
  width: 80px;
  height: 3px;
  background: linear-gradient(45deg, #1976d2, #42a5f5);
  border-radius: 2px;
}

.breadcrumbs-container {
  border-radius: 8px;
  padding: 12px 16px;
  transition: all 0.3s ease;
}

.theme--light .breadcrumbs-container {
  background-color: #f8f9fa;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
}

.theme--dark .breadcrumbs-container {
  background-color: rgba(30, 30, 30, 0.7);
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
}

.breadcrumbs {
  display: flex;
  flex-wrap: wrap;
  padding: 0;
  margin: 0;
  list-style: none;
  align-items: center;
}

.breadcrumb-item {
  display: flex;
  align-items: center;
  font-size: 14px;
  white-space: nowrap;
}

.breadcrumb-link {
  display: flex;
  align-items: center;
  text-decoration: none;
  transition: all 0.2s ease;
  font-weight: 500;
  padding: 4px 8px;
  border-radius: 4px;
}

.theme--light .breadcrumb-link {
  color: #5c6bc0;
}

.theme--dark .breadcrumb-link {
  color: #7986cb;
}

.theme--light .breadcrumb-link:hover {
  color: #3f51b5;
  background-color: rgba(63, 81, 181, 0.08);
}

.theme--dark .breadcrumb-link:hover {
  color: #9fa8da;
  background-color: rgba(121, 134, 203, 0.15);
}

.breadcrumb-text {
  display: flex;
  align-items: center;
  font-weight: 600;
  padding: 4px 8px;
}

.theme--light .breadcrumb-text {
  color: #424242;
}

.theme--dark .breadcrumb-text {
  color: #e0e0e0;
}

.breadcrumb-icon {
  margin-right: 6px;
}

.breadcrumb-divider {
  display: flex;
  align-items: center;
  margin: 0 2px;
}

.theme--light .breadcrumb-divider {
  color: #bdbdbd;
}

.theme--dark .breadcrumb-divider {
  color: #616161;
}

.chevron-icon {
  font-size: 18px;
}

.theme--light .chevron-icon {
  color: #9e9e9e;
}

.theme--dark .chevron-icon {
  color: #757575;
}

.active .breadcrumb-link {
  font-weight: 600;
}

.theme--light .active .breadcrumb-link,
.theme--light .active .breadcrumb-text {
  color: #424242;
}

.theme--dark .active .breadcrumb-link,
.theme--dark .active .breadcrumb-text {
  color: #e0e0e0;
}

.theme--light .active .breadcrumb-text {
  background-color: rgba(0, 0, 0, 0.03);
  border-radius: 4px;
}

.theme--dark .active .breadcrumb-text {
  background-color: rgba(255, 255, 255, 0.05);
  border-radius: 4px;
}

.v-theme--dark .v-sheet {
  background-color: #2c2c2c !important;
  color: #ffffff !important;
}

.v-theme--dark .v-chip {
  background-color: #1976d2 !important;
  color: #ffffff !important;
}

.v-theme--dark .filter-btn {
  background-color: #1e1e1e !important;
  color: #ffffff !important;
  border-color: #424242 !important;
}

@media (max-width: 768px) {
  .breadcrumbs-container {
    padding: 8px 12px;
  }

  .breadcrumb-item {
    font-size: 13px;
  }
}

@media (max-width: 600px) {
  .breadcrumb-icon {
    margin-right: 4px;
  }

  .breadcrumb-divider {
    margin: 0;
  }

  .breadcrumb-link,
  .breadcrumb-text {
    padding: 3px 4px;
  }

  .filter-toggle-container {
    top: auto;
    bottom: 24px;
    left: 24px;
    transform: none;
  }
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

@media (min-width: 1920px) {
  .container-custom {
    max-width: 1600px;
  }
}
</style>
