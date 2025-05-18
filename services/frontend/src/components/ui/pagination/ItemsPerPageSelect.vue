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
import { computed, onMounted, watch } from 'vue';
import { useUserPreferencesStore } from '@/stores/userPreferences';
import { useRoute, useRouter } from 'vue-router';

const props = defineProps({
  options: {
    type: Array,
    default: () => [8, 12, 16, 20]
  }
});

const emit = defineEmits(['update:perPage']);
const preferencesStore = useUserPreferencesStore();
const route = useRoute();
const router = useRouter();

onMounted(() => {
  if (route.query.per_page) {
    const perPage = parseInt(route.query.per_page);
    if (props.options.includes(perPage)) {
      preferencesStore.setItemsPerPage(perPage);
    }
  }
  else if (preferencesStore.itemsPerPage !== 12) {
    updateUrlWithPerPage(preferencesStore.itemsPerPage);
  }
});

const updateUrlWithPerPage = (perPage) => {
  router.replace({
    query: {
      ...route.query,
      per_page: perPage
    }
  });
};

const selectedValue = computed({
  get: () => preferencesStore.itemsPerPage,
  set: (value) => {
    preferencesStore.setItemsPerPage(value);
    updateUrlWithPerPage(value);
    emit('update:perPage', value);
  }
});

watch(() => route.query.per_page, (newPerPage) => {
  if (newPerPage) {
    const perPage = parseInt(newPerPage);
    if (props.options.includes(perPage) && perPage !== preferencesStore.itemsPerPage) {
      preferencesStore.setItemsPerPage(perPage);
    }
  }
});
</script>

<style scoped>
.items-per-page-select {
  margin-left: auto;
}
</style>
