<template>
  <v-select
      v-model="selectedOrdering"
      :items="sortOptions"
      label="Sort by"
      density="compact"
      variant="outlined"
      style="max-width: 220px;"
      class="product-sorting-select"
  ></v-select>
</template>

<script setup>
import {computed} from 'vue';
import {useCatalogStore} from '@/stores/catalog';

const props = defineProps({
  options: {
    type: Array,
    default: () => [
      {title: 'Newest first', value: '-id'},
      {title: 'Oldest first', value: 'id'},
      {title: 'Latest collections first', value: '-year'},
      {title: 'Earliest collections first', value: 'year'}
    ]
  }
});

const emit = defineEmits(['update:ordering']);
const catalogStore = useCatalogStore();

const sortOptions = computed(() => {
  return props.options.map(option => ({
    title: option.title,
    value: option.value
  }));
});

const selectedOrdering = computed({
  get: () => catalogStore.currentOrdering,
  set: (value) => {
    catalogStore.setOrdering(value);
    emit('update:ordering', value);
  }
});
</script>

<style scoped>
.product-sorting-select {
  margin-right: auto;
}
</style>
