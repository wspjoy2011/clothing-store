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
import {computed, inject} from 'vue';

const props = defineProps({
  options: {
    type: Array,
    default: () => [
      {title: 'Newest first', value: '-id'},
      {title: 'Oldest first', value: 'id'},
      {title: 'Latest collections first', value: '-year'},
      {title: 'Earliest collections first', value: 'year'},
      {title: 'Price: Low to High', value: 'price'},
      {title: 'Price: High to Low', value: '-price'}
    ]
  }
});

const emit = defineEmits(['update:ordering']);

const store = inject('filterStore');

const sortOptions = computed(() => {
  return props.options.map(option => ({
    title: option.title,
    value: option.value
  }));
});

const selectedOrdering = computed({
  get: () => store.value.currentOrdering,
  set: (value) => {
    store.value.setOrdering(value);
    emit('update:ordering', value);
  }
});
</script>
