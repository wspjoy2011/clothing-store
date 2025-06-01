<template>
  <v-expansion-panel>
    <v-expansion-panel-title>Gender</v-expansion-panel-title>
    <v-expansion-panel-text>
      <div v-if="filtersLoading" class="d-flex justify-center py-2">
        <v-progress-circular
            indeterminate
            size="24"
            color="primary"
        ></v-progress-circular>
      </div>

      <div v-else-if="!availableGenders || availableGenders.length === 0" class="text-center py-2">
        No options available
      </div>

      <div v-else>
        <v-checkbox
            v-for="gender in availableGenders"
            :key="gender"
            v-model="selectedGenders"
            :label="formatGender(gender)"
            :value="gender"
            density="compact"
            hide-details
            class="mt-1"
        ></v-checkbox>

        <div v-if="hasSelectedGenders" class="d-flex justify-end mt-2">
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

const selectedGenders = ref([]);

const availableFilters = inject('availableFilters', null);
const categoryAvailableFilters = inject('categoryAvailableFilters', null);
const activeFilters = inject('activeFilters', null);
const isLoadingFilters = inject('isLoadingFilters', false);

const currentAvailableFilters = computed(() => {
  return categoryAvailableFilters?.value || availableFilters?.value;
});

const availableGenders = computed(() => {
  if (currentAvailableFilters.value?.gender) {
    return currentAvailableFilters.value.gender.values;
  }
  return [];
});

const filtersLoading = computed(() => isLoadingFilters?.value || false);

const hasSelectedGenders = computed(() => selectedGenders.value.length > 0);

const formatGender = (gender) => {
  return gender.charAt(0).toUpperCase() + gender.slice(1);
};

const clearSelection = () => {
  selectedGenders.value = [];
};

watch(selectedGenders, (newVal) => {
  if (!activeFilters) return;

  let genderFilter = null;
  if (newVal.length > 0) {
    genderFilter = newVal.join(',');
  }

  activeFilters.value.gender = genderFilter;
});

watch(() => activeFilters?.value?.gender, (newVal) => {
  if (newVal === null) {
    selectedGenders.value = [];
  } else if (newVal && newVal !== selectedGenders.value.join(',')) {
    selectedGenders.value = newVal.split(',');
  }
}, {immediate: true});
</script>
