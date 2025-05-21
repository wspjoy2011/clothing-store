import { watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useCatalogStore } from '@/stores/catalog';


export function useProductRouting(createQueryFromFilters, ensureValidPage) {
  const router = useRouter();
  const route = useRoute();
  const catalogStore = useCatalogStore();

  watch(() => route.query, (newQuery, oldQuery) => {
    const filterParamsChanged =
        newQuery.gender !== oldQuery.gender ||
        newQuery.min_year !== oldQuery.min_year ||
        newQuery.max_year !== oldQuery.max_year ||
        newQuery.q !== oldQuery.q;

    if (filterParamsChanged) {
      catalogStore.loadFiltersFromQuery(newQuery);
    }

    const pageChanged = newQuery.page !== oldQuery.page;
    const orderingChanged = newQuery.ordering !== oldQuery.ordering;
    const perPageChanged = newQuery.per_page !== oldQuery.per_page;

    if (filterParamsChanged || pageChanged || orderingChanged || perPageChanged) {
      const page = parseInt(newQuery.page) || 1;
      const ordering = newQuery.ordering || '-id';

      catalogStore.fetchProducts(page, ordering).then(() => {
        const validPage = ensureValidPage(page);
        if (validPage !== page) {
          router.push({
            name: 'catalog',
            query: {
              ...createQueryFromFilters(),
              page: validPage > 1 ? validPage : undefined,
              ordering: catalogStore.currentOrdering !== '-id' ? catalogStore.currentOrdering : undefined,
              per_page: newQuery.per_page
            }
          });

          catalogStore.fetchProducts(validPage, ordering);
        }
      });
    }
  }, {deep: true});

  const initialize = () => {
    const page = parseInt(route.query.page) || 1;
    const ordering = route.query.ordering || '-id';

    catalogStore.fetchFilters().then(() => {
      catalogStore.loadFiltersFromQuery(route.query);

      catalogStore.fetchProducts(page, ordering).then(() => {
        const validPage = ensureValidPage(page);
        if (validPage !== page) {
          router.push({
            name: 'catalog',
            query: {
              ...createQueryFromFilters(),
              page: validPage > 1 ? validPage : undefined,
              ordering: ordering !== '-id' ? ordering : undefined,
              per_page: route.query.per_page
            }
          });

          catalogStore.fetchProducts(validPage, ordering);
        }
      });
    });
  };

  const cleanup = () => {
    catalogStore.resetState();
  };

  return {
    initialize,
    cleanup
  };
}
