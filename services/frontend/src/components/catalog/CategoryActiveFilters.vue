<template>
  <v-row v-if="hasActiveFilters && !isLoading" class="mb-4">
    <v-col cols="12">
      <v-sheet rounded class="pa-3" color="grey-lighten-4">
        <div class="d-flex align-center justify-space-between">
          <div class="d-flex align-center flex-wrap">
            <v-icon icon="mdi-filter-variant" class="mr-2"/>
            <span class="text-body-1 mr-2">Active Filters</span>

            <v-chip
                v-if="activeFilters.gender"
                size="small"
                class="ml-2 mb-1"
                closable
                @click:close="clearGenderFilter"
            >
              Gender: {{ activeFilters.gender }}
            </v-chip>

            <v-chip
                v-if="activeFilters.min_year || activeFilters.max_year"
                size="small"
                class="ml-2 mb-1"
                closable
                @click:close="clearYearFilter"
            >
              Year: {{
                activeFilters.min_year || availableFilters.year?.min
              }}-{{
                activeFilters.max_year || availableFilters.year?.max
              }}
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
</template>

<script setup>
defineProps({
  hasActiveFilters: {
    type: Boolean,
    required: true
  },
  isLoading: {
    type: Boolean,
    required: true
  },
  isLoadingFilters: {
    type: Boolean,
    required: true
  },
  activeFilters: {
    type: Object,
    required: true
  },
  availableFilters: {
    type: Object,
    required: true
  }
});

const emit = defineEmits(['clear-all-filters', 'clear-gender-filter', 'clear-year-filter']);

const clearGenderFilter = () => {
  emit('clear-gender-filter');
};

const clearYearFilter = () => {
  emit('clear-year-filter');
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
