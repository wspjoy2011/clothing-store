import { useRouter } from 'vue-router';
import { useCatalogStore } from '@/stores/catalog';


export function useProductSorting(createQueryFromFilters) {
  const router = useRouter();
  const catalogStore = useCatalogStore();

  const handleOrderingChange = (ordering) => {
    const query = createQueryFromFilters();

    router.push({
      name: 'catalog',
      query: {
        ...query,
        page: undefined,
        ordering: ordering !== '-id' ? ordering : undefined
      }
    });

    catalogStore.setOrdering(ordering);
    catalogStore.fetchProducts(1, ordering);
  };

  return {
    handleOrderingChange
  };
}
