<template>
  <v-sheet class="filter-sheet" rounded>

    <!-- Gender Filter -->
    <div class="mb-6">
      <h4 class="text-subtitle-1 mb-2">Gender</h4>
      <v-checkbox
        v-model="selectedGender.men"
        label="Men"
        density="compact"
        hide-details
        color="primary"
        class="mt-1"
      ></v-checkbox>
      <v-checkbox
        v-model="selectedGender.women"
        label="Women"
        density="compact"
        hide-details
        color="primary"
        class="mt-1"
      ></v-checkbox>
    </div>

    <!-- Year Range Filter -->
    <div class="mb-6">
      <h4 class="text-subtitle-1 mb-2">Year Range</h4>
      <div class="year-inputs mb-3">
        <v-text-field
          v-model.number="yearRange[0]"
          type="number"
          density="compact"
          hide-details
          variant="outlined"
          label="From"
          @change="validateYearRange"
          class="year-input"
        ></v-text-field>

        <div class="year-separator mx-1 mx-sm-2">—</div>

        <v-text-field
          v-model.number="yearRange[1]"
          type="number"
          density="compact"
          hide-details
          variant="outlined"
          label="To"
          @change="validateYearRange"
          class="year-input"
        ></v-text-field>
      </div>

      <v-range-slider
        v-model="yearRange"
        :min="2020"
        :max="2023"
        step="1"
        hide-details
        color="primary"
        thumb-label="none"
        class="mt-1"
      ></v-range-slider>
    </div>

    <!-- Active Filters Chips -->
    <div v-if="hasActiveFilters" class="active-filters-section mb-6">
      <h4 class="text-subtitle-1 mb-2">Active Filters</h4>
      <div class="d-flex flex-wrap">
        <v-chip
          v-if="selectedGender.men"
          size="small"
          class="mr-1 mb-1 mr-sm-2 mb-sm-2"
          closable
          @click:close="selectedGender.men = false"
        >
          Men
        </v-chip>
        <v-chip
          v-if="selectedGender.women"
          size="small"
          class="mr-1 mb-1 mr-sm-2 mb-sm-2"
          closable
          @click:close="selectedGender.women = false"
        >
          Women
        </v-chip>
        <v-chip
          v-if="!isDefaultYearRange"
          size="small"
          class="mr-1 mb-1 mr-sm-2 mb-sm-2"
          closable
          @click:close="resetYearRange"
        >
          {{ yearRange[0] }}-{{ yearRange[1] }}
        </v-chip>
      </div>
    </div>

    <!-- Filter Actions -->
    <div class="filter-actions">
      <v-btn
        variant="outlined"
        @click="clearFilters"
        size="small"
        class="btn-action"
      >
        Clear
      </v-btn>
      <v-btn
        color="primary"
        @click="applyFilters"
        size="small"
        class="btn-action"
      >
        Apply
      </v-btn>
    </div>
  </v-sheet>
</template>

<script setup>
import { ref, computed } from 'vue';

const selectedGender = ref({
  men: false,
  women: false
});

const yearRange = ref([2020, 2023]);

const hasActiveFilters = computed(() => {
  return selectedGender.value.men ||
         selectedGender.value.women ||
         !isDefaultYearRange.value;
});

const isDefaultYearRange = computed(() => {
  return yearRange.value[0] === 2020 &&
         yearRange.value[1] === 2023;
});

function validateYearRange() {
  if (yearRange.value[0] > yearRange.value[1]) {
    yearRange.value = [yearRange.value[1], yearRange.value[0]];
  }

  yearRange.value[0] = Math.max(2020, Math.min(2023, yearRange.value[0]));
  yearRange.value[1] = Math.max(2020, Math.min(2023, yearRange.value[1]));
}

function resetYearRange() {
  yearRange.value = [2020, 2023];
}

function clearFilters() {
  selectedGender.value.men = false;
  selectedGender.value.women = false;
  resetYearRange();
}

function applyFilters() {
  console.log('Filters applied:', {
    gender: {
      men: selectedGender.value.men,
      women: selectedGender.value.women
    },
    yearRange: yearRange.value
  });
}
</script>

<style scoped>
.filter-sheet {
  padding: 14px 14px;
  height: 100%;
}

.year-inputs {
  display: flex;
  align-items: center;
}

.year-input {
  flex: 1;
  min-width: 0;
}

.year-separator {
  font-size: 16px;
  color: rgba(0, 0, 0, 0.6);
  font-weight: 500;
  text-align: center;
  flex-shrink: 0;
}

.active-filters-section {
  margin-top: 16px;
}

.filter-actions {
  display: flex;
  justify-content: space-between;
  margin-top: 20px;
  gap: 8px;
}

.btn-action {
  flex: 1;
  min-width: 0;
}

:deep(.v-theme--dark) .year-separator {
  color: rgba(255, 255, 255, 0.6);
}

@media (max-width: 1200px) {
  .filter-sheet {
    padding: 12px 10px;
  }

  .year-inputs {
    flex-wrap: wrap;
  }
}

@media (max-width: 960px) {
  .filter-sheet {
    padding: 10px 8px;
  }
}

@media (max-width: 768px) {
  .year-inputs {
    flex-direction: row;
  }

  .year-input {
    width: calc(50% - 10px);
  }

  .year-separator {
    font-size: 14px;
  }
}

@media (max-width: 600px) {
  .filter-sheet {
    padding: 8px 6px;
  }

  .year-inputs {
    flex-direction: column;
    align-items: stretch;
  }

  .year-input {
    width: 100%;
  }

  .year-separator {
    margin: 4px 0;
    text-align: center;
    width: 100%;
  }
}

@media (max-width: 480px) {
  h3 {
    font-size: 1.1rem !important;
  }

  h4 {
    font-size: 0.95rem !important;
  }

  .filter-actions {
    flex-direction: column;
    gap: 6px;
  }

  .filter-sheet {
    padding: 6px 4px;
  }
}
</style>
