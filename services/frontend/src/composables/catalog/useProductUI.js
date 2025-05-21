import { computed } from 'vue';
import { useCatalogStore } from '@/stores/catalog';


export function useProductUI() {
  const catalogStore = useCatalogStore();

  const hasProducts = computed(() =>
    !catalogStore.loading &&
    !catalogStore.error &&
    catalogStore.products.length > 0
  );

  const isEmpty = computed(() =>
    !catalogStore.loading &&
    !catalogStore.error &&
    catalogStore.products.length === 0
  );

  return {
    hasProducts,
    isEmpty
  };
}
