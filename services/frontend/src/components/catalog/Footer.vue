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
          :current-page="currentPage"
          :total-pages="totalPages"
          @update:page="handlePageChange"
      />
    </v-col>
  </v-row>
</template>

<script setup>
import {computed, inject} from 'vue';
import AppPagination from '@/components/ui/pagination/AppPagination.vue';
import NoItemsFound from '@/components/ui/empty-states/NoItemsFound.vue';

const props = defineProps({
  isEmpty: {
    type: Boolean,
    required: true
  },
  hasItems: {
    type: Boolean,
    required: true
  }
});

const paginationData = inject('paginationData', null);
const paginationHandlers = inject('paginationHandlers', null);

const currentPage = computed(() => {
  return paginationData?.value?.currentPage || 1;
});

const totalPages = computed(() => {
  return paginationData?.value?.totalPages || 0;
});

const handlePageChange = (page) => {
  if (paginationHandlers?.value?.handlePageChange) {
    paginationHandlers.value.handlePageChange(page);
  } else {
    console.error('No pagination handler found');
  }
};
</script>
