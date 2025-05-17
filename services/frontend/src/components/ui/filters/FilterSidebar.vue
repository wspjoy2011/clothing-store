<template>
  <v-card class="filter-sidebar">
    <v-card-text class="pa-0">
      <v-alert
        v-if="catalogStore.filtersError"
        type="error"
        variant="tonal"
        density="compact"
        class="ma-3"
      >
        Failed to load filters
      </v-alert>

      <div v-if="catalogStore.hasActiveFilters" class="d-flex justify-end px-4 py-2">
        <v-btn
          variant="text"
          density="compact"
          color="primary"
          size="small"
          @click="clearFilters"
        >
          Clear All
        </v-btn>
      </div>

      <v-expansion-panels variant="accordion" multiple>
        <gender-filter v-if="hasGenderFilter"></gender-filter>
        <year-range-filter v-if="hasYearFilter"></year-range-filter>
      </v-expansion-panels>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { computed, inject } from 'vue';
import { useCatalogStore } from '@/stores/catalog';
import GenderFilter from './GenderFilter.vue';
import YearRangeFilter from './YearRangeFilter.vue';

const catalogStore = useCatalogStore();
const clearAllFilters = inject('clearAllFilters');

const hasGenderFilter = computed(() => true);
const hasYearFilter = computed(() => true);

const clearFilters = () => {
  if (clearAllFilters) {
    clearAllFilters();
  }
};
</script>

<style scoped>
.filter-sidebar {
  height: 100%;
  position: sticky;
  top: 24px;
}
</style>
