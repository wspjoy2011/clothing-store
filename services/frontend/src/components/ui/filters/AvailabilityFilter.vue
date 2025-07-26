<template>
  <v-expansion-panel>
    <v-expansion-panel-title>
      <span>Availability</span>
      <span v-if="!filtersLoading && availabilityData" class="text-caption text-medium-emphasis ml-2">
        ({{ totalCount }})
      </span>
    </v-expansion-panel-title>
    <v-expansion-panel-text>
      <div v-if="filtersLoading" class="d-flex justify-center py-2">
        <v-progress-circular
            indeterminate
            size="24"
            color="primary"
        ></v-progress-circular>
      </div>

      <div v-else-if="!availabilityData" class="text-center py-2">
        No availability data
      </div>

      <div v-else>
        <!-- All items option -->
        <v-checkbox
            v-model="isAvailable"
            :value="null"
            density="compact"
            hide-details
            class="mt-1"
        >
          <template v-slot:label>
            <div class="d-flex align-center">
              <v-icon
                color="primary"
                size="small"
                class="me-2"
              >
                mdi-view-list
              </v-icon>
              <span>All items</span>
              <v-chip
                size="x-small"
                variant="outlined"
                color="primary"
                class="ml-2"
              >
                {{ totalCount }}
              </v-chip>
            </div>
          </template>
        </v-checkbox>

        <!-- Available only option -->
        <v-checkbox
            v-model="isAvailable"
            :value="true"
            density="compact"
            hide-details
            class="mt-1"
        >
          <template v-slot:label>
            <div class="d-flex align-center">
              <v-icon
                color="success"
                size="small"
                class="me-2"
              >
                mdi-check-circle
              </v-icon>
              <span>Available only</span>
              <v-chip
                size="x-small"
                variant="outlined"
                color="success"
                class="ml-2"
              >
                {{ availabilityData.available_count }}
              </v-chip>
            </div>
          </template>
        </v-checkbox>

        <!-- Unavailable only option -->
        <v-checkbox
            v-model="isAvailable"
            :value="false"
            density="compact"
            hide-details
            class="mt-1"
        >
          <template v-slot:label>
            <div class="d-flex align-center">
              <v-icon
                color="error"
                size="small"
                class="me-2"
              >
                mdi-close-circle
              </v-icon>
              <span>Unavailable only</span>
              <v-chip
                size="x-small"
                variant="outlined"
                color="error"
                class="ml-2"
              >
                {{ availabilityData.unavailable_count }}
              </v-chip>
            </div>
          </template>
        </v-checkbox>

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
const availableFilters = inject('availableFilters', null);
const categoryAvailableFilters = inject('categoryAvailableFilters', null);
const isLoadingFilters = inject('isLoadingFilters', false);

const currentAvailableFilters = computed(() => {
  return categoryAvailableFilters?.value || availableFilters?.value;
});

const filtersLoading = computed(() => isLoadingFilters?.value || false);

const availabilityData = computed(() => {
  return currentAvailableFilters.value?.is_available;
});

const totalCount = computed(() => {
  if (!availabilityData.value) return 0;
  return availabilityData.value.available_count + availabilityData.value.unavailable_count;
});

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

<style scoped>
.text-caption {
  font-size: 0.75rem;
}

.text-medium-emphasis {
  opacity: 0.6;
}
</style>
