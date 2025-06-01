import {provide, watch, computed} from 'vue';
import {useRouter} from 'vue-router';
import {useCatalogStore} from '@/stores/catalog';


export function useProductFiltering(route) {
    const router = useRouter();
    const catalogStore = useCatalogStore();

    const createQueryFromFilters = () => {
        const query = {...route.query};
        const activeFilters = catalogStore.activeFilters;
        const availableFilters = catalogStore.availableFilters;

        if (activeFilters.gender !== null) {
            query.gender = activeFilters.gender;
        } else {
            delete query.gender;
        }

        if (
            availableFilters?.year &&
            activeFilters.min_year !== null &&
            activeFilters.min_year !== availableFilters.year.min
        ) {
            query.min_year = activeFilters.min_year;
        } else {
            delete query.min_year;
        }

        if (
            availableFilters?.year &&
            activeFilters.max_year !== null &&
            activeFilters.max_year !== availableFilters.year.max
        ) {
            query.max_year = activeFilters.max_year;
        } else {
            delete query.max_year;
        }

        if (catalogStore.searchQuery && catalogStore.searchQuery.trim()) {
            query.q = catalogStore.searchQuery.trim();
        } else {
            delete query.q;
        }

        return query;
    };

    const clearAllFilters = () => {
        const drawerWasOpen = catalogStore.isFilterDrawerOpen;

        catalogStore.clearFilters();

        const newQuery = {};
        if (route.query.ordering && route.query.ordering !== '-id') {
            newQuery.ordering = route.query.ordering;
        }
        if (route.query.per_page) {
            newQuery.per_page = route.query.per_page;
        }
        if (route.query.q) {
            newQuery.q = route.query.q;
        }

        router.push({
            name: 'catalog',
            query: newQuery
        }).then(() => {
            catalogStore.fetchProducts(1);

            if (drawerWasOpen) {
                catalogStore.toggleFilterDrawer(true);
            }
        });
    };

    provide('clearAllFilters', clearAllFilters);
    provide('availableFilters', computed(() => catalogStore.availableFilters));
    provide('activeFilters', computed(() => catalogStore.activeFilters));
    provide('hasActiveFilters', computed(() => catalogStore.hasActiveFilters));
    provide('filtersError', computed(() => catalogStore.filtersError));
    provide('isLoadingFilters', computed(() => catalogStore.filtersLoading));

    watch(() => catalogStore.activeFilters, () => {
        if (catalogStore.isUpdatingFilters) return;

        const drawerWasOpen = catalogStore.isFilterDrawerOpen;

        router.push({
            name: 'catalog',
            query: {
                ...createQueryFromFilters(),
                page: undefined,
                ordering: catalogStore.currentOrdering !== '-id' ? catalogStore.currentOrdering : undefined,
                per_page: route.query.per_page
            }
        }).then(() => {
            catalogStore.fetchProducts(1);

            if (drawerWasOpen) {
                catalogStore.toggleFilterDrawer(true);
            }
        });
    }, {deep: true});

    return {
        createQueryFromFilters,
        clearAllFilters
    };
}
