<template>
  <!-- Filter Drawer -->
  <v-navigation-drawer
      v-model="catalogStore.isFilterDrawerOpen"
      location="left"
      temporary
      width="320"
      class="filter-drawer"
  >
    <div class="drawer-header">
      <h3 class="text-h6">Filters</h3>
      <v-btn
          icon="mdi-close"
          variant="text"
          size="small"
          @click="catalogStore.toggleFilterDrawer(false)"
      />
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
        @click="catalogStore.toggleFilterDrawer(true)"
    >
      <v-badge
          :content="catalogStore.activeFiltersCount"
          :value="catalogStore.activeFiltersCount > 0"
          :color="catalogStore.activeFiltersCount > 0 ? 'error' : 'primary'"
          location="top end"
      />
    </v-btn>
  </div>
</template>

<script setup>
import {useCatalogStore} from '@/stores/catalog';
import FilterSidebar from '@/components/ui/filters/FilterSidebar.vue';

const catalogStore = useCatalogStore();

defineProps({
  hasProducts: {
    type: Boolean,
    required: true
  }
});
</script>

<style scoped>
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

.v-theme--dark .filter-btn {
  background-color: #1e1e1e !important;
  color: #ffffff !important;
  border-color: #424242 !important;
}

@media (max-width: 600px) {
  .filter-toggle-container {
    top: auto;
    bottom: 24px;
    left: 24px;
    transform: none;
  }
}
</style>
