<template>
  <div class="header mb-6">
    <!-- Title section -->
    <div class="text-center">
      <h1 class="text-h4 font-weight-bold mb-2">
        {{ title }}
      </h1>

      <!-- Decorative divider for category pages -->
      <div v-if="showDivider" class="divider-container">
        <div class="divider-line"></div>
      </div>

      <!-- Description for category pages -->
      <p v-if="description" class="text-subtitle-1 mt-4 mx-auto" style="max-width: 800px;">
        {{ description }}
      </p>
    </div>

    <!-- Search results indicator -->
    <div v-if="searchQuery && searchQuery.trim()" class="text-center" :class="showDivider ? 'mt-6' : 'mb-6'">
      <v-chip
          color="primary"
          variant="outlined"
          size="large"
          closable
          @click:close="clearSearch"
          prepend-icon="mdi-magnify"
      >
        Search results for: "{{ searchQuery }}"
      </v-chip>
    </div>

    <!-- Control panel -->
    <v-row v-if="hasProducts" justify="center" align="center" :class="showDivider ? 'mt-6 mb-3' : 'mb-3'">
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
  </div>
</template>

<script setup>
import ProductSorting from '@/components/ui/sorting/ProductSorting.vue';
import ItemsPerPageSelect from '@/components/ui/pagination/ItemsPerPageSelect.vue';
import {computed} from "vue";

const props = defineProps({
  store: {
    type: Object,
    required: true
  },
  title: {
    type: String,
    required: true
  },
  description: {
    type: String,
    default: null
  },
  showDivider: {
    type: Boolean,
    default: false
  },
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

const searchQuery = computed(() => props.store.searchQuery);

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

<style scoped>
.header {
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  padding-bottom: 16px;
}

.divider-container {
  display: flex;
  justify-content: center;
  margin-top: 16px;
}

.divider-line {
  width: 80px;
  height: 3px;
  background: linear-gradient(45deg, #1976d2, #42a5f5);
  border-radius: 2px;
}
</style>
