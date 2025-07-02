<template>
  <v-row justify="center">
    <v-col cols="12">
      <h1 class="text-h4 font-weight-bold mb-2 text-center">Fashion & Accessories Catalog</h1>

      <!-- Search results indicator -->
      <div v-if="catalogStore.searchQuery" class="text-center mb-6">
        <v-chip
            color="primary"
            variant="outlined"
            size="large"
            closable
            @click:close="clearSearch"
            prepend-icon="mdi-magnify"
        >
          Search results for: "{{ catalogStore.searchQuery }}"
        </v-chip>
      </div>
    </v-col>
  </v-row>

  <!-- Control panel -->
  <v-row v-if="hasProducts" justify="center" align="center" class="mb-3">
    <v-col cols="12" sm="6" md="4" lg="3">
      <product-sorting @update:ordering="handleOrderingChange"/>
    </v-col>

    <v-spacer class="d-none d-md-flex"></v-spacer>

    <v-col cols="12" sm="6" md="4" lg="3" class="d-flex justify-end">
      <items-per-page-select
          :options="itemsPerPageOptions"
          @update:perPage="handleItemsPerPageChange"
      />
    </v-col>
  </v-row>
</template>

<script setup>
import {useCatalogStore} from '@/stores/catalog';
import ProductSorting from '@/components/ui/sorting/ProductSorting.vue';
import ItemsPerPageSelect from '@/components/ui/pagination/ItemsPerPageSelect.vue';

const catalogStore = useCatalogStore();

defineProps({
  hasProducts: {
    type: Boolean,
    required: true
  },
  itemsPerPageOptions: {
    type: Array,
    required: true
  }
});

const emit = defineEmits([
  'clear-search',
  'update:ordering',
  'update:per-page'
]);

const clearSearch = () => {
  emit('clear-search');
};

const handleOrderingChange = (ordering) => {
  emit('update:ordering', ordering);
};

const handleItemsPerPageChange = (perPage) => {
  emit('update:per-page', perPage);
};
</script>
