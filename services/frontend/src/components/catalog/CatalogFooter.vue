<template>
  <!-- No products found -->
  <no-items-found
      v-if="isEmpty"
      title="No products found"
      message="Try adjusting your filters or search query"
      icon="mdi-search-off"
  />

  <!-- Pagination -->
  <v-row justify="center" v-if="hasItems">
    <v-col cols="12" class="px-0">
      <app-pagination
          :current-page="catalogStore.currentPage"
          :total-pages="catalogStore.totalPages"
          @update:page="handlePageChange"
      />
    </v-col>
  </v-row>
</template>

<script setup>
import {useCatalogStore} from '@/stores/catalog';
import AppPagination from '@/components/ui/pagination/AppPagination.vue';
import NoItemsFound from '@/components/ui/empty-states/NoItemsFound.vue';

const catalogStore = useCatalogStore();

defineProps({
  isEmpty: {
    type: Boolean,
    required: true
  },
  hasItems: {
    type: Boolean,
    required: true
  }
});

const emit = defineEmits(['update:page']);

const handlePageChange = (page) => {
  emit('update:page', page);
};
</script>
