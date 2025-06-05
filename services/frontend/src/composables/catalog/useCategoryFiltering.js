import {computed, watch, provide, ref} from 'vue';
import {useRouter} from 'vue-router';
import {useCategoryStore} from '@/stores/categoryStore';

export function useCategoryFiltering(route, fetchProducts) {
    const router = useRouter();
    const categoryStore = useCategoryStore();

    const isChangingCategory = ref(false);

    const createQueryFromFilters = () => {
        const query = {...route.query};

        if (categoryStore.activeFilters.gender !== null) {
            query.gender = categoryStore.activeFilters.gender;
        } else {
            delete query.gender;
        }

        if (
            categoryStore.availableFilters?.year &&
            categoryStore.activeFilters.min_year !== null &&
            categoryStore.activeFilters.min_year !== categoryStore.availableFilters.year.min
        ) {
            query.min_year = categoryStore.activeFilters.min_year;
        } else {
            delete query.min_year;
        }

        if (
            categoryStore.availableFilters?.year &&
            categoryStore.activeFilters.max_year !== null &&
            categoryStore.activeFilters.max_year !== categoryStore.availableFilters.year.max
        ) {
            query.max_year = categoryStore.activeFilters.max_year;
        } else {
            delete query.max_year;
        }

        if (categoryStore.searchQuery && categoryStore.searchQuery.trim()) {
            query.q = categoryStore.searchQuery.trim();
        } else {
            delete query.q;
        }

        return query;
    };

    const clearAllFilters = () => {
        const drawerWasOpen = categoryStore.isFilterDrawerOpen;

        categoryStore.clearFilters();

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

        const routeName = route.name;
        const params = {...route.params};

        router.push({
            name: routeName,
            params,
            query: newQuery
        }).then(() => {
            if (fetchProducts) {
                fetchProducts(1, route.query.ordering || '-id');
            }

            if (drawerWasOpen) {
                categoryStore.toggleFilterDrawer(true);
            }
        });
    };

    provide('clearAllFilters', clearAllFilters);
    provide('categoryAvailableFilters', computed(() => categoryStore.availableFilters));
    provide('activeFilters', computed(() => categoryStore.activeFilters));
    provide('hasActiveFilters', computed(() => categoryStore.hasActiveFilters));
    provide('filtersError', computed(() => categoryStore.filtersError));
    provide('isLoadingFilters', computed(() => categoryStore.filtersLoading));

    watch(() => categoryStore.activeFilters, () => {
        if (categoryStore.isUpdatingFilters || isChangingCategory.value) return;

        const drawerWasOpen = categoryStore.isFilterDrawerOpen;

        router.push({
            name: route.name,
            params: {...route.params},
            query: {
                ...createQueryFromFilters(),
                page: undefined,
                ordering: route.query.ordering !== '-id' ? route.query.ordering : undefined,
                per_page: route.query.per_page
            }
        }).then(() => {
            if (fetchProducts) {
                fetchProducts(1, route.query.ordering || '-id');
            }

            if (drawerWasOpen) {
                categoryStore.toggleFilterDrawer(true);
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
        availableFilters: computed(() => categoryStore.availableFilters),
        activeFilters: computed(() => categoryStore.activeFilters),
        searchQuery: computed(() => categoryStore.searchQuery),
        isFilterDrawerOpen: computed(() => categoryStore.isFilterDrawerOpen),
        isUpdatingFilters: computed(() => categoryStore.isUpdatingFilters),

        hasActiveFilters: computed(() => categoryStore.hasActiveFilters),
        activeFiltersCount: computed(() => categoryStore.activeFiltersCount),

        setAvailableFilters: (filters) => {
            categoryStore.availableFilters = filters || {gender: null, year: null};
        },
        clearAvailableFilters: () => categoryStore.resetCategoryFilters(),
        clearFilters: () => categoryStore.clearFilters(),
        clearSearch: () => categoryStore.clearSearch(),
        toggleFilterDrawer: (state) => categoryStore.toggleFilterDrawer(state),
        loadFiltersFromQuery: (query) => categoryStore.loadFiltersFromQuery(query),
        createQueryFromFilters,
        clearAllFilters,
        disableFilterWatcher,
        enableFilterWatcher
    };
}
