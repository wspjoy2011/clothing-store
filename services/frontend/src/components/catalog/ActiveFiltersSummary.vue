<template>
  <v-row v-if="catalogStore.hasActiveFilters && !catalogStore.loading" class="mb-4">
    <v-col cols="12">
      <v-sheet rounded class="pa-3" color="grey-lighten-4">
        <div class="d-flex align-center justify-space-between">
          <div class="d-flex align-center flex-wrap">
            <v-icon icon="mdi-filter-variant" class="mr-2"/>
            <span class="text-body-1 mr-2">Active Filters</span>

            <v-chip
                v-if="catalogStore.activeFilters.gender"
                size="small"
                class="ml-2 mb-1"
                closable
                @click:close="clearGenderFilter"
            >
              Gender: {{ catalogStore.activeFilters.gender }}
            </v-chip>

            <v-chip
                v-if="catalogStore.activeFilters.min_year || catalogStore.activeFilters.max_year"
                size="small"
                class="ml-2 mb-1"
                closable
                @click:close="clearYearFilter"
            >
              Year: {{
                catalogStore.activeFilters.min_year || catalogStore.availableFilters.year?.min
              }}-{{
                catalogStore.activeFilters.max_year || catalogStore.availableFilters.year?.max
              }}
            </v-chip>

            <v-progress-circular
                v-if="catalogStore.filtersLoading"
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
              :disabled="catalogStore.filtersLoading"
          >
            Clear All
          </v-btn>
        </div>
      </v-sheet>
    </v-col>
  </v-row>
</template>

<script setup>
import {useCatalogStore} from '@/stores/catalog';

const catalogStore = useCatalogStore();

const emit = defineEmits(['clear-all-filters']);

const clearGenderFilter = () => {
  catalogStore.activeFilters.gender = null;
};

const clearYearFilter = () => {
  catalogStore.activeFilters.min_year = null;
  catalogStore.activeFilters.max_year = null;
};

const clearAllFilters = () => {
  emit('clear-all-filters');
};
</script>

<style scoped>
.v-theme--dark .v-sheet {
  background-color: #2c2c2c !important;
  color: #ffffff !important;
}

.v-theme--dark .v-chip {
  background-color: #1976d2 !important;
  color: #ffffff !important;
}
</style>
