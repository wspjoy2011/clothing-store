import {computed, watch} from 'vue';
import {useRouter} from 'vue-router';
import {useCatalogStore} from '@/stores/catalog';
import {useUserPreferencesStore} from '@/stores/userPreferences';


export function useProductPagination(createQueryFromFilters, route) {
    const router = useRouter();
    const catalogStore = useCatalogStore();
    const preferencesStore = useUserPreferencesStore();

    const itemsPerPageOptions = [8, 12, 16, 20];

    const hasItems = computed(() =>
        !catalogStore.loading &&
        !catalogStore.error &&
        catalogStore.totalPages > 0
    );

    const ensureValidPage = (page) => {
        if (catalogStore.totalPages > 0 && page > catalogStore.totalPages) {
            return catalogStore.totalPages;
        }
        return page;
    };

    const handlePageChange = (page) => {
        const validPage = ensureValidPage(page);
        const query = createQueryFromFilters();

        router.push({
            name: 'catalog',
            query: {
                ...query,
                page: validPage > 1 ? validPage : undefined
            }
        });

        catalogStore.fetchProducts(validPage);
    };

    const handleItemsPerPageChange = (count) => {
        const query = createQueryFromFilters();

        preferencesStore.setItemsPerPage(count);

        catalogStore.fetchProducts(1).then(() => {
            if (catalogStore.currentPage > catalogStore.totalPages) {
                const correctedPage = catalogStore.totalPages > 0 ? catalogStore.totalPages : 1;

                router.push({
                    name: 'catalog',
                    query: {
                        ...query,
                        page: correctedPage > 1 ? correctedPage : undefined,
                        per_page: count
                    }
                });

                if (correctedPage !== 1) {
                    catalogStore.fetchProducts(correctedPage);
                }
            } else {
                router.push({
                    name: 'catalog',
                    query: {
                        ...query,
                        page: undefined,
                        per_page: count
                    }
                });
            }
        });
    };

    watch(() => preferencesStore.itemsPerPage, () => {
        if (catalogStore.totalItems > 0) {
            const validPage = ensureValidPage(catalogStore.currentPage);
            if (validPage !== catalogStore.currentPage) {
                catalogStore.fetchProducts(validPage);
            } else {
                catalogStore.fetchProducts(catalogStore.currentPage);
            }
        }
    });

    return {
        itemsPerPageOptions,
        hasItems,
        ensureValidPage,
        handlePageChange,
        handleItemsPerPageChange
    };
}
