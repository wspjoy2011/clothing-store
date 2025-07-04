import {computed, watch, provide} from 'vue';
import {useRouter} from 'vue-router';
import {useUserPreferencesStore} from '@/stores/userPreferences';

/**
 * Universal product pagination composable
 * @param {Object} store - Store instance (catalogStore or categoryStore)
 * @param {Function} createQueryFromFilters - Function to create query from filters
 * @param {Object} route - Vue route object
 * @param {Object} options - Configuration options
 * @returns {Object} Pagination utilities
 */
export function useProductPagination(store, createQueryFromFilters, route, options = {}) {
    const router = useRouter();
    const preferencesStore = useUserPreferencesStore();

    const {
        routeName = 'catalog',
        fetchMethod = 'fetchProducts'
    } = options;

    const itemsPerPageOptions = [8, 12, 16, 20];

    const hasItems = computed(() =>
        !store.loading &&
        !store.error &&
        store.totalPages > 0
    );

    const ensureValidPage = (page) => {
        if (store.totalPages > 0 && page > store.totalPages) {
            return store.totalPages;
        }
        return page;
    };

    const handlePageChange = (page) => {
        const validPage = ensureValidPage(page);
        const query = createQueryFromFilters();

        const routeParams = routeName === 'category' ? {...route.params} : {};

        router.push({
            name: routeName,
            ...(routeName === 'category' && {params: routeParams}),
            query: {
                ...query,
                page: validPage > 1 ? validPage : undefined
            }
        });

        store[fetchMethod](validPage);
    };

    const handleItemsPerPageChange = (count) => {
        const query = createQueryFromFilters();
        const routeParams = routeName === 'category' ? {...route.params} : {};

        preferencesStore.setItemsPerPage(count);

        store[fetchMethod](1).then(() => {
            if (store.currentPage > store.totalPages) {
                const correctedPage = store.totalPages > 0 ? store.totalPages : 1;

                router.push({
                    name: routeName,
                    ...(routeName === 'category' && {params: routeParams}),
                    query: {
                        ...query,
                        page: correctedPage > 1 ? correctedPage : undefined,
                        per_page: count
                    }
                });

                if (correctedPage !== 1) {
                    store[fetchMethod](correctedPage);
                }
            } else {
                router.push({
                    name: routeName,
                    ...(routeName === 'category' && {params: routeParams}),
                    query: {
                        ...query,
                        page: undefined,
                        per_page: count
                    }
                });
            }
        });
    };

    const paginationData = computed(() => ({
        currentPage: store.currentPage || 1,
        totalPages: store.totalPages || 0,
        totalItems: store.totalItems || 0,
        hasItems: hasItems.value,
        itemsPerPageOptions
    }));

    const paginationHandlers = computed(() => ({
        handlePageChange,
        handleItemsPerPageChange
    }));

    provide('paginationData', paginationData);
    provide('paginationHandlers', paginationHandlers);

    watch(() => preferencesStore.itemsPerPage, () => {
        if (store.totalItems > 0) {
            const validPage = ensureValidPage(store.currentPage);
            if (validPage !== store.currentPage) {
                store[fetchMethod](validPage);
            } else {
                store[fetchMethod](store.currentPage);
            }
        }
    });

    return {
        itemsPerPageOptions,
        hasItems,
        ensureValidPage,
        handlePageChange,
        handleItemsPerPageChange,
        paginationData,
        paginationHandlers
    };
}
