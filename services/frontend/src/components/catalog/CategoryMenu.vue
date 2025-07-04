<template>
  <div class="category-menu" :class="{ 'theme-dark': isDarkTheme }">
    <div v-if="isLoading" class="d-flex justify-center pa-4">
      <v-progress-circular indeterminate color="primary" />
    </div>

    <div v-else-if="hasError" class="text-center text-error pa-4">
      {{ hasError }}
    </div>

    <div v-else-if="!categoriesExist" class="text-center pa-4">
      No categories available
    </div>

    <div v-else class="category-menu-container">
      <category-menu-item
        v-for="category in categoriesData"
        :key="`${category.type}-${category.id}`"
        :item="category"
        @item-click="handleCategoryClick"
        class="menu-item-vertical"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useTheme } from 'vuetify';
import { useCategoryStore } from '@/stores/categoryStore';
import CategoryMenuItem from './CategoryMenuItem.vue';

const props = defineProps({
  propCategories: {
    type: Array,
    default: null
  },
  propLoading: {
    type: Boolean,
    default: null
  },
  propError: {
    type: [String, Object],
    default: null
  },
  propHasCategories: {
    type: Boolean,
    default: null
  }
});

const theme = useTheme();
const categoryStore = useCategoryStore();

const storeLoading = ref(false);
const storeError = ref(null);

const isDarkTheme = computed(() => {
  return theme.global.current.value.dark;
});

const categoriesData = computed(() => {
  return props.propCategories !== null ? props.propCategories : categoryStore.categories;
});

const isLoading = computed(() => {
  return props.propLoading !== null ? props.propLoading : storeLoading.value;
});

const hasError = computed(() => {
  return props.propError !== null ? props.propError : storeError.value;
});

const categoriesExist = computed(() => {
  return props.propHasCategories !== null ? props.propHasCategories : categoryStore.categories.length > 0;
});

const handleCategoryClick = (categoryInfo) => {
  console.log('Category clicked:', categoryInfo);
  categoryStore.navigateToCategory(categoryInfo);
};

const loadFromStore = async () => {
  storeLoading.value = true;

  try {
    await categoryStore.fetchCategoryMenu();
    storeError.value = categoryStore.error;
  } catch (error) {
    storeError.value = error.message || 'Failed to load categories';
  } finally {
    storeLoading.value = false;
  }
};

onMounted(() => {
  if (props.propCategories === null && !props.propHasCategories && !props.propLoading) {
    loadFromStore();
  }
});
</script>

<style scoped>
.category-menu {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

.category-menu-container {
  display: flex;
  flex-direction: column;
  padding: 12px;
  max-width: 360px;
  background-color: white;
}

.menu-item-vertical {
  margin-bottom: 8px;
}

.menu-item-vertical:last-child {
  margin-bottom: 0;
}

.theme-dark {
  background-color: #1E1E1E !important;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2) !important;
}

.theme-dark .category-menu-container {
  background-color: #1E1E1E !important;
}

.theme-dark .category-submenu-card {
  background-color: #1E1E1E !important;
}

.theme-dark .nested-item-title:hover {
  background-color: rgba(80, 80, 80, 0.3);
}

.theme-dark .category-btn {
  background-color: #2A2A2A;
}
</style>
