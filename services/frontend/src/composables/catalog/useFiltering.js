import {provide, watch, computed, ref} from 'vue';
import {useRouter} from 'vue-router';

export function useFiltering(route, store, options = {}) {
    const router = useRouter();
    const {
        routeName = 'catalog',
        fetchProducts = null,
        provideKey = 'availableFilters'
    } = options;
    
    const isChangingCategory = ref(false);
    const isClearingFilters = ref(false);

    const createQueryFromFilters = () => {
        const query = {...route.query};
        const activeFilters = store.activeFilters;
        const availableFilters = store.availableFilters;

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

        if (store.searchQuery && store.searchQuery.trim()) {
            query.q = store.searchQuery.trim();
        } else {
            delete query.q;
        }

        return query;
    };

    const clearAllFilters = () => {
        if (isClearingFilters.value) {
            return;
        }

        isClearingFilters.value = true;

        const drawerWasOpen = store.isFilterDrawerOpen;

        store.clearAllFilters();

        const newQuery = {};
        if (route.query.ordering && route.query.ordering !== '-id') {
            newQuery.ordering = route.query.ordering;
        }
        if (route.query.per_page) {
            newQuery.per_page = route.query.per_page;
        }

        const routeConfig = {
            name: routeName === 'catalog' ? routeName : route.name,
            query: newQuery
        };

        if (routeName !== 'catalog') {
            routeConfig.params = {...route.params};
        }

        router.push(routeConfig).then(() => {
            if (fetchProducts) {
                fetchProducts(1, route.query.ordering || '-id');
            } else {
                store.fetchProducts(1);
            }

            if (drawerWasOpen) {
                store.toggleFilterDrawer(true);
            }

            setTimeout(() => {
                isClearingFilters.value = false;
            }, 100);
        }).catch(error => {
            isClearingFilters.value = false;
        });
    };

    provide('clearAllFilters', clearAllFilters);
    provide(provideKey, computed(() => store.availableFilters));
    provide('activeFilters', computed(() => store.activeFilters));
    provide('hasActiveFilters', computed(() => store.hasActiveFilters));
    provide('filtersError', computed(() => store.filtersError));
    provide('isLoadingFilters', computed(() => store.filtersLoading));

    watch(() => store.activeFilters, () => {
        if (isChangingCategory.value || isClearingFilters.value) return;

        const drawerWasOpen = store.isFilterDrawerOpen;

        const routeConfig = {
            query: {
                ...createQueryFromFilters(),
                page: undefined,
                ordering: route.query.ordering !== '-id' ? route.query.ordering : undefined,
                per_page: route.query.per_page
            }
        };

        if (routeName === 'catalog') {
            routeConfig.name = 'catalog';
        } else {
            routeConfig.name = route.name;
            routeConfig.params = {...route.params};
        }

        router.push(routeConfig).then(() => {
            if (fetchProducts) {
                fetchProducts(1, route.query.ordering || '-id');
            } else {
                store.fetchProducts(1);
            }

            if (drawerWasOpen) {
                store.toggleFilterDrawer(true);
            }
        });
    }, {deep: true});

    const disableFilterWatcher = () => {
        isChangingCategory.value = true;
    };

    const enableFilterWatcher = () => {
        isChangingCategory.value = false;
    };

    return {
        createQueryFromFilters,
        clearAllFilters,
        disableFilterWatcher,
        enableFilterWatcher
    };
}
