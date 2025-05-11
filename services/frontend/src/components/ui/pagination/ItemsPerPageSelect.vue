<template>
  <v-select
      v-model="selectedValue"
      :items="props.options"
      label="Items per page"
      density="compact"
      variant="outlined"
      style="max-width: 100px;"
      class="items-per-page-select"
  ></v-select>
</template>

<script setup>
import {computed} from 'vue';
import {useUserPreferencesStore} from '@/stores/userPreferences';

const props = defineProps({
  options: {
    type: Array,
    default: () => [8, 12, 16, 20]
  }
});

const emit = defineEmits(['update:perPage']);
const preferencesStore = useUserPreferencesStore();

const selectedValue = computed({
  get: () => preferencesStore.itemsPerPage,
  set: (value) => {
    preferencesStore.setItemsPerPage(value);
    emit('update:perPage', value);
  }
});
</script>

<style scoped>
.items-per-page-select {
  margin-left: auto;
}
</style>
