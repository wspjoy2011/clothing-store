<template>
  <v-row v-if="filterStore.hasActiveFilters && !filterStore.loading" class="mb-4">
    <v-col cols="12">
      <v-sheet rounded class="pa-3" color="grey-lighten-4">
        <div class="d-flex align-center justify-space-between">
          <div class="d-flex align-center flex-wrap">
            <v-icon icon="mdi-filter-variant" class="mr-2"/>
            <span class="text-body-1 mr-2">Active Filters</span>

            <v-chip
                v-if="filterStore.activeFilters.gender"
                size="small"
                class="ml-2 mb-1"
                closable
                @click:close="clearGenderFilter"
            >
              Gender: {{ filterStore.activeFilters.gender }}
            </v-chip>

            <v-chip
                v-if="filterStore.activeFilters.min_year || filterStore.activeFilters.max_year"
                size="small"
                class="ml-2 mb-1"
                closable
                @click:close="clearYearFilter"
            >
              Year: {{
                filterStore.activeFilters.min_year || filterStore.availableFilters.year?.min
              }}-{{
                filterStore.activeFilters.max_year || filterStore.availableFilters.year?.max
              }}
            </v-chip>

            <v-progress-circular
                v-if="filterStore.filtersLoading"
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
              :disabled="filterStore.filtersLoading"
          >
            Clear All
          </v-btn>
        </div>
      </v-sheet>
    </v-col>
  </v-row>
</template>

<script setup>
import {inject} from 'vue';

const props = defineProps({
  filterStore: {
    type: Object,
    required: true
  }
});

const clearAllFiltersFromProvider = inject('clearAllFilters', null);

const clearGenderFilter = () => {
  props.filterStore.clearGenderFilter();
};

const clearYearFilter = () => {
  props.filterStore.clearYearFilter();
};

const clearAllFilters = () => {
  if (clearAllFiltersFromProvider) {
    clearAllFiltersFromProvider();
  } else {
    props.filterStore.clearAllFilters();
  }
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
