import { useRouter, useRoute } from 'vue-router';
import { useUserPreferencesStore } from '@/stores/userPreferences';

export function useProductSorting(createQueryFromFilters) {
  const router = useRouter();
  const route = useRoute();
  const preferencesStore = useUserPreferencesStore();

  const handleOrderingChange = (ordering) => {
    const query = createQueryFromFilters();

    preferencesStore.setProductOrdering(ordering);

    const routeName = route.name;
    const routeParams = routeName === 'catalog' ? {} : { ...route.params };

    router.push({
      name: routeName,
      ...(routeName !== 'catalog' && { params: routeParams }),
      query: {
        ...query,
        page: undefined,
        ordering: ordering !== '-id' ? ordering : undefined,
        per_page: route.query.per_page
      }
    });
  };

  return {
    handleOrderingChange
  };
}
