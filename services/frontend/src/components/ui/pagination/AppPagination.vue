<template>
  <v-row v-if="props.totalPages > 0">
    <v-col cols="12" class="d-flex justify-center mt-6">
      <v-pagination
          :model-value="props.currentPage"
          :length="props.totalPages"
          :total-visible="props.totalVisible"
          rounded
          @update:model-value="updatePage"
      ></v-pagination>
    </v-col>
  </v-row>
</template>

<script setup>
import { inject } from 'vue';

const props = defineProps({
  currentPage: {
    type: Number,
    required: true
  },
  totalPages: {
    type: Number,
    required: true
  },
  totalVisible: {
    type: Number,
    default: 7
  }
});

const emit = defineEmits(['update:page']);

const categoryHandlers = inject('categoryPaginationHandlers', null);

const updatePage = (page) => {
  if (categoryHandlers?.handlePageChange) {
    categoryHandlers.handlePageChange(page);
  } else {
    emit('update:page', page);
  }
};
</script>
