<template>
  <v-expansion-panel>
    <v-expansion-panel-title>
      <span>Gender</span>
      <span v-if="!filtersLoading && genderData && genderData.values.length > 0"
            class="text-caption text-medium-emphasis ml-2">
        ({{ totalGenderCount }})
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

      <div v-else-if="!availableGenders || availableGenders.length === 0" class="text-center py-2">
        No options available
      </div>

      <div v-else>
        <v-checkbox
            v-for="gender in availableGenders"
            :key="gender"
            v-model="selectedGenders"
            :value="gender"
            density="compact"
            hide-details
            class="mt-1"
        >
          <template v-slot:label>
            <div class="d-flex align-center">
              <v-icon
                  :color="getGenderColor(gender)"
                  size="small"
                  class="me-2"
              >
                {{ getGenderIcon(gender) }}
              </v-icon>
              <span>{{ formatGender(gender) }}</span>
              <v-chip
                  size="x-small"
                  variant="outlined"
                  :color="getGenderColor(gender)"
                  class="ml-2"
              >
                {{ getGenderCount(gender) }}
              </v-chip>
            </div>
          </template>
        </v-checkbox>

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

const genderData = computed(() => {
  return currentAvailableFilters.value?.gender;
});

const availableGenders = computed(() => {
  return genderData.value?.values || [];
});

const filtersLoading = computed(() => isLoadingFilters?.value || false);

const hasSelectedGenders = computed(() => selectedGenders.value.length > 0);

const totalGenderCount = computed(() => {
  if (!genderData.value || !genderData.value.count) return 0;
  return Object.values(genderData.value.count).reduce((sum, count) => sum + count, 0);
});

const formatGender = (gender) => {
  return gender.charAt(0).toUpperCase() + gender.slice(1);
};

const getGenderCount = (gender) => {
  return genderData.value?.count?.[gender] || 0;
};

const getGenderIcon = (gender) => {
  const genderLower = gender.toLowerCase();
  switch (genderLower) {
    case 'men':
      return 'mdi-account';
    case 'women':
      return 'mdi-account-outline';
    case 'boys':
      return 'mdi-account-child';
    case 'girls':
      return 'mdi-account-child-outline';
    case 'unisex':
      return 'mdi-account-multiple';
    default:
      return 'mdi-account-question';
  }
};

const getGenderColor = (gender) => {
  const genderLower = gender.toLowerCase();
  switch (genderLower) {
    case 'men':
      return 'blue';
    case 'women':
      return 'pink';
    case 'boys':
      return 'light-blue';
    case 'girls':
      return 'purple';
    case 'unisex':
      return 'orange';
    default:
      return 'grey';
  }
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

<style scoped>
.text-caption {
  font-size: 0.75rem;
}

.text-medium-emphasis {
  opacity: 0.6;
}
</style>
