import { watch } from 'vue';
import { useRouter } from 'vue-router';
import { useCatalogStore } from '@/stores/catalog';


export function useProductSearch(createQueryFromFilters, route) {
  const router = useRouter();
  const catalogStore = useCatalogStore();

  const clearSearch = () => {
    catalogStore.clearSearch();

    const query = {...route.query};
    delete query.q;
    delete query.page;

    router.push({
      name: 'catalog',
      query
    }).then(() => {
      catalogStore.fetchFilters().then(() => {
        catalogStore.fetchProducts(1);
      });
    });
  };

  watch(() => catalogStore.searchQuery, (newValue, oldValue) => {
    if (newValue !== oldValue && !catalogStore.isUpdatingFilters) {
      const query = createQueryFromFilters();

      catalogStore.fetchFilters().then(() => {
        router.push({
          name: 'catalog',
          query: {
            ...query,
            page: undefined,
            ordering: catalogStore.currentOrdering !== '-id' ? catalogStore.currentOrdering : undefined,
            per_page: route.query.per_page
          }
        }).then(() => {
          catalogStore.fetchProducts(1);
        });
      });
    }
  });

  return {
    clearSearch
  };
}
