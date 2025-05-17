<template>
  <v-expansion-panel>
    <v-expansion-panel-title>Year</v-expansion-panel-title>
    <v-expansion-panel-text>
      <div v-if="filtersLoading" class="d-flex justify-center py-2">
        <v-progress-circular
            indeterminate
            size="24"
            color="primary"
        ></v-progress-circular>
      </div>

      <div v-else-if="!hasYearRange" class="text-center py-2">
        No year range available
      </div>

      <div v-else>
        <!-- Year inputs  -->
        <div class="d-flex align-center mb-4">
          <v-text-field
            v-model="minYearInput"
            type="number"
            variant="outlined"
            density="compact"
            hide-details
            :min="minYear"
            :max="maxYear"
            @change="handleMinYearChange"
            class="year-input"
          ></v-text-field>

          <span class="mx-2">—</span>

          <v-text-field
            v-model="maxYearInput"
            type="number"
            variant="outlined"
            density="compact"
            hide-details
            :min="minYear"
            :max="maxYear"
            @change="handleMaxYearChange"
            class="year-input"
          ></v-text-field>
        </div>

        <!-- Slider -->
        <v-range-slider
            v-model="rangeValue"
            :min="minYear"
            :max="maxYear"
            :step="1"
            color="primary"
            track-color="grey-lighten-3"
            hide-details
            density="compact"
        ></v-range-slider>

        <div v-if="isFiltered" class="d-flex justify-end mt-2">
          <v-btn
              variant="text"
              density="compact"
              color="primary"
              size="small"
              @click="resetRange"
          >
            Reset
          </v-btn>
        </div>
      </div>
    </v-expansion-panel-text>
  </v-expansion-panel>
</template>

<script setup>
import {ref, computed, watch} from 'vue';
import {useCatalogStore} from '@/stores/catalog';

const catalogStore = useCatalogStore();
const rangeValue = ref([0, 0]);
const minYearInput = ref('');
const maxYearInput = ref('');

const filtersLoading = computed(() => catalogStore.filtersLoading);

const hasYearRange = computed(() => {
  return catalogStore.availableFilters?.year &&
      catalogStore.availableFilters.year.min !== null &&
      catalogStore.availableFilters.year.max !== null;
});

const minYear = computed(() => {
  return hasYearRange.value ? catalogStore.availableFilters.year.min : 0;
});

const maxYear = computed(() => {
  return hasYearRange.value ? catalogStore.availableFilters.year.max : 0;
});

const isFiltered = computed(() => {
  if (!hasYearRange.value) return false;
  return rangeValue.value[0] !== minYear.value || rangeValue.value[1] !== maxYear.value;
});

const handleMinYearChange = () => {
  let minVal = parseInt(minYearInput.value);

  if (isNaN(minVal)) {
    minVal = minYear.value;
  } else {
    minVal = Math.max(minYear.value, Math.min(maxYear.value, minVal));
  }

  minYearInput.value = minVal.toString();

  if (minVal <= rangeValue.value[1]) {
    rangeValue.value = [minVal, rangeValue.value[1]];
  } else {
    rangeValue.value = [minVal, minVal];
    maxYearInput.value = minVal.toString();
  }
};

const handleMaxYearChange = () => {
  let maxVal = parseInt(maxYearInput.value);

  if (isNaN(maxVal)) {
    maxVal = maxYear.value;
  } else {
    maxVal = Math.max(minYear.value, Math.min(maxYear.value, maxVal));
  }

  maxYearInput.value = maxVal.toString();

  if (maxVal >= rangeValue.value[0]) {
    rangeValue.value = [rangeValue.value[0], maxVal];
  } else {
    rangeValue.value = [maxVal, maxVal];
    minYearInput.value = maxVal.toString();
  }
};

const resetRange = () => {
  if (hasYearRange.value) {
    rangeValue.value = [minYear.value, maxYear.value];
    minYearInput.value = minYear.value.toString();
    maxYearInput.value = maxYear.value.toString();
  }
};

watch(() => catalogStore.availableFilters.year, (newYearFilter) => {
  if (newYearFilter && newYearFilter.min !== null && newYearFilter.max !== null) {
    rangeValue.value = [newYearFilter.min, newYearFilter.max];
    minYearInput.value = newYearFilter.min.toString();
    maxYearInput.value = newYearFilter.max.toString();
  }
}, {immediate: true});

watch(rangeValue, (newVal) => {
  if (hasYearRange.value) {
    minYearInput.value = newVal[0].toString();
    maxYearInput.value = newVal[1].toString();

    if (newVal[0] !== catalogStore.activeFilters.min_year ||
        newVal[1] !== catalogStore.activeFilters.max_year) {
      catalogStore.setFilter('year', newVal);
    }
  }
}, {deep: true});

watch([
  () => catalogStore.activeFilters.min_year,
  () => catalogStore.activeFilters.max_year
], ([newMin, newMax]) => {
  if (hasYearRange.value) {
    if (newMin === null && newMax === null) {
      resetRange();
    } else if (newMin !== null && newMax !== null &&
      (rangeValue.value[0] !== newMin || rangeValue.value[1] !== newMax)) {
      rangeValue.value = [newMin, newMax];
      minYearInput.value = newMin.toString();
      maxYearInput.value = newMax.toString();
    }
  }
}, {immediate: true});

</script>

<style scoped>
.year-input {
  max-width: 100px;
}
</style>
