<template>
  <v-expansion-panel>
    <v-expansion-panel-title>Price Range</v-expansion-panel-title>
    <v-expansion-panel-text>
      <div v-if="filtersLoading" class="d-flex justify-center py-2">
        <v-progress-circular
            indeterminate
            size="24"
            color="primary"
        ></v-progress-circular>
      </div>

      <div v-else-if="!hasPriceRange" class="text-center py-2">
        No price range available
      </div>

      <div v-else>
        <!-- Price inputs -->
        <div class="d-flex align-center mb-4">
          <v-text-field
              v-model="minPriceInput"
              type="number"
              variant="outlined"
              density="compact"
              hide-details
              :min="minPrice"
              :max="maxPrice"
              step="0.01"
              prefix="$"
              @change="handleMinPriceChange"
              class="price-input"
          ></v-text-field>

          <span class="mx-2">—</span>

          <v-text-field
              v-model="maxPriceInput"
              type="number"
              variant="outlined"
              density="compact"
              hide-details
              :min="minPrice"
              :max="maxPrice"
              step="0.01"
              prefix="$"
              @change="handleMaxPriceChange"
              class="price-input"
          ></v-text-field>
        </div>

        <!-- Slider -->
        <v-range-slider
            v-model="rangeValue"
            :min="minPrice"
            :max="maxPrice"
            :step="0.01"
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
import {ref, computed, watch, inject} from 'vue';

const rangeValue = ref([0, 0]);
const minPriceInput = ref('');
const maxPriceInput = ref('');

const availableFilters = inject('availableFilters', null);
const categoryAvailableFilters = inject('categoryAvailableFilters', null);
const activeFilters = inject('activeFilters', null);
const isLoadingFilters = inject('isLoadingFilters', false);

const currentAvailableFilters = computed(() => {
  return categoryAvailableFilters?.value || availableFilters?.value;
});

const filtersLoading = computed(() => isLoadingFilters?.value || false);

const hasPriceRange = computed(() => {
  return currentAvailableFilters.value?.price &&
      currentAvailableFilters.value.price.min !== null &&
      currentAvailableFilters.value.price.max !== null;
});

const minPrice = computed(() => {
  return hasPriceRange.value ? currentAvailableFilters.value.price.min : 0;
});

const maxPrice = computed(() => {
  return hasPriceRange.value ? currentAvailableFilters.value.price.max : 1000;
});

const isFiltered = computed(() => {
  return activeFilters?.value?.min_price !== null || activeFilters?.value?.max_price !== null;
});

watch(hasPriceRange, (hasRange) => {
  if (hasRange) {
    const currentMin = activeFilters?.value?.min_price || minPrice.value;
    const currentMax = activeFilters?.value?.max_price || maxPrice.value;

    rangeValue.value = [currentMin, currentMax];
    minPriceInput.value = currentMin.toString();
    maxPriceInput.value = currentMax.toString();
  }
}, { immediate: true });

watch(rangeValue, (newRange) => {
  if (!activeFilters) return;

  const [min, max] = newRange;
  minPriceInput.value = min.toString();
  maxPriceInput.value = max.toString();

  activeFilters.value.min_price = min !== minPrice.value ? min : null;
  activeFilters.value.max_price = max !== maxPrice.value ? max : null;
});

const handleMinPriceChange = () => {
  const value = parseFloat(minPriceInput.value);
  if (!isNaN(value)) {
    rangeValue.value = [Math.max(minPrice.value, Math.min(value, rangeValue.value[1])), rangeValue.value[1]];
  }
};

const handleMaxPriceChange = () => {
  const value = parseFloat(maxPriceInput.value);
  if (!isNaN(value)) {
    rangeValue.value = [rangeValue.value[0], Math.min(maxPrice.value, Math.max(value, rangeValue.value[0]))];
  }
};

const resetRange = () => {
  rangeValue.value = [minPrice.value, maxPrice.value];
  minPriceInput.value = minPrice.value.toString();
  maxPriceInput.value = maxPrice.value.toString();
};

watch(() => activeFilters?.value?.min_price, (newVal) => {
  if (newVal !== null && newVal !== rangeValue.value[0]) {
    rangeValue.value = [newVal, rangeValue.value[1]];
    minPriceInput.value = newVal.toString();
  }
}, { immediate: true });

watch(() => activeFilters?.value?.max_price, (newVal) => {
  if (newVal !== null && newVal !== rangeValue.value[1]) {
    rangeValue.value = [rangeValue.value[0], newVal];
    maxPriceInput.value = newVal.toString();
  }
}, { immediate: true });
</script>

<style scoped>
.price-input {
  max-width: 120px;
}
</style>
