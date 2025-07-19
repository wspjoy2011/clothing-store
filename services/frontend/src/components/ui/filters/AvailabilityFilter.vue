<template>
  <v-expansion-panel>
    <v-expansion-panel-title>Availability</v-expansion-panel-title>
    <v-expansion-panel-text>
      <div v-if="filtersLoading" class="d-flex justify-center py-2">
        <v-progress-circular
            indeterminate
            size="24"
            color="primary"
        ></v-progress-circular>
      </div>

      <div v-else>
        <v-checkbox
            v-model="isAvailable"
            label="Available only"
            density="compact"
            hide-details
            class="mt-1"
        ></v-checkbox>

        <div v-if="isAvailable !== null" class="d-flex justify-end mt-2">
          <v-btn
              variant="text"
              density="compact"
              color="primary"
              size="small"
              @click="clearSelection"
          >
            Clear
          </v-btn>
        </div>
      </div>
    </v-expansion-panel-text>
  </v-expansion-panel>
</template>

<script setup>
import {ref, computed, watch, inject} from 'vue';

const isAvailable = ref(null);

const activeFilters = inject('activeFilters', null);
const isLoadingFilters = inject('isLoadingFilters', false);

const filtersLoading = computed(() => isLoadingFilters?.value || false);

const clearSelection = () => {
  isAvailable.value = null;
};

watch(isAvailable, (newVal) => {
  if (!activeFilters) return;
  activeFilters.value.is_available = newVal;
});

watch(() => activeFilters?.value?.is_available, (newVal) => {
  if (newVal !== isAvailable.value) {
    isAvailable.value = newVal;
  }
}, {immediate: true});
</script>
