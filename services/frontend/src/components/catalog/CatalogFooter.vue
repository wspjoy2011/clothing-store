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
          :current-page="currentPageValue"
          :total-pages="totalPagesValue"
          @update:page="handlePageChange"
      />
    </v-col>
  </v-row>
</template>

<script setup>
import {computed} from 'vue';
import {useCatalogStore} from '@/stores/catalog';
import AppPagination from '@/components/ui/pagination/AppPagination.vue';
import NoItemsFound from '@/components/ui/empty-states/NoItemsFound.vue';

const catalogStore = useCatalogStore();

const props = defineProps({
  isEmpty: {
    type: Boolean,
    required: true
  },
  hasItems: {
    type: Boolean,
    required: true
  },
  currentPage: {
    type: Number,
    default: null
  },
  totalPages: {
    type: Number,
    default: null
  }
});

const emit = defineEmits(['update:page']);

const currentPageValue = computed(() => {
  return props.currentPage !== null ? props.currentPage : catalogStore.currentPage;
});

const totalPagesValue = computed(() => {
  return props.totalPages !== null ? props.totalPages : catalogStore.totalPages;
});

const handlePageChange = (page) => {
  emit('update:page', page);
};
</script>
