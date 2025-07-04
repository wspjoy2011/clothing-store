import {ref, computed, provide} from 'vue';
import {useRouter} from 'vue-router';
import {useCategoryStore} from '@/stores/categoryStore';
import categoryService from '@/services/categoryService';

export function useCategoryProducts(route) {
    const router = useRouter();
    const categoryStore = useCategoryStore();

    const isLoading = ref(true);
    const error = ref(null);
    const products = ref([]);
    const totalPages = ref(0);
    const totalItems = ref(0);
    const currentPage = ref(1);

    const isLoadingFilters = ref(false);
    const filtersError = ref(null);

    const masterCategoryId = computed(() => {
        const slug = route.params.masterCategory;
        return slug ? categoryStore.getMasterCategoryIdBySlug(slug) : null;
    });

    const subCategoryId = computed(() => {
        if (!masterCategoryId.value || !route.params.subCategory) return null;
        return categoryStore.getSubCategoryIdBySlug(masterCategoryId.value, route.params.subCategory);
    });

    const articleTypeId = computed(() => {
        if (!masterCategoryId.value || !subCategoryId.value || !route.params.articleType) return null;
        return categoryStore.getArticleTypeIdBySlug(masterCategoryId.value, subCategoryId.value, route.params.articleType);
    });

    const itemsPerPageOptions = [8, 12, 16, 20];

    const hasProducts = computed(() =>
        !isLoading.value && !error.value && products.value.length > 0
    );

    const isEmpty = computed(() =>
        !isLoading.value && !error.value && products.value.length === 0
    );

    const hasItems = computed(() =>
        !isLoading.value && !error.value && totalPages.value > 0
    );

    const ensureValidPage = (page) => {
        if (totalPages.value > 0 && page > totalPages.value) {
            return totalPages.value;
        }
        return page;
    };

    const fetchCategoryProducts = async (page = 1, ordering = '-id') => {
        if (!masterCategoryId.value) return;

        isLoading.value = true;
        error.value = null;

        try {
            const filters = {};
            if (categoryStore.activeFilters.gender) filters.gender = categoryStore.activeFilters.gender;
            if (categoryStore.activeFilters.min_year) filters.min_year = categoryStore.activeFilters.min_year;
            if (categoryStore.activeFilters.max_year) filters.max_year = categoryStore.activeFilters.max_year;

            const result = await categoryService.getProductsByCategory(
                masterCategoryId.value,
                subCategoryId.value,
                articleTypeId.value,
                page,
                route.query.per_page || 12,
                ordering,
                filters,
                categoryStore.searchQuery
            );

            products.value = result.products;
            totalPages.value = result.total_pages;
            totalItems.value = result.total_items;
            currentPage.value = page;

            return result;
        } catch (err) {
            error.value = err;
        } finally {
            isLoading.value = false;
        }
    };

    const fetchCategoryFilters = async () => {
        if (!masterCategoryId.value) {
            categoryStore.setAvailableFilters({gender: null, year: null});
            return;
        }

        isLoadingFilters.value = true;
        filtersError.value = null;

        try {
            const filters = await categoryService.getFiltersByCategory(
                masterCategoryId.value,
                subCategoryId.value,
                articleTypeId.value
            );

            categoryStore.setAvailableFilters(filters || {gender: null, year: null});
        } catch (err) {
            filtersError.value = err;
            categoryStore.setAvailableFilters({gender: null, year: null});
        } finally {
            isLoadingFilters.value = false;
        }
    };

    const handlePageChange = (createQueryFromFilters) => (page) => {
        const validPage = ensureValidPage(page);
        const query = createQueryFromFilters();

        const routeName = route.name;
        const params = {...route.params};

        router.push({
            name: routeName,
            params,
            query: {
                ...query,
                page: validPage > 1 ? validPage : undefined,
                ordering: route.query.ordering !== '-id' ? route.query.ordering : undefined,
                per_page: route.query.per_page
            }
        }).then(() => {
            fetchCategoryProducts(validPage, route.query.ordering || '-id');
        });
    };

    const handleItemsPerPageChange = (createQueryFromFilters) => (count) => {
        const query = createQueryFromFilters();
        const routeName = route.name;
        const params = {...route.params};

        router.push({
            name: routeName,
            params,
            query: {
                ...query,
                page: undefined,
                per_page: count,
                ordering: route.query.ordering !== '-id' ? route.query.ordering : undefined
            }
        }).then(() => {
            fetchCategoryProducts(1, route.query.ordering || '-id');
        });
    };

    const handleOrderingChange = (createQueryFromFilters) => (ordering) => {
        const query = createQueryFromFilters();
        const routeName = route.name;
        const params = {...route.params};

        router.push({
            name: routeName,
            params,
            query: {
                ...query,
                page: undefined,
                ordering: ordering !== '-id' ? ordering : undefined,
                per_page: route.query.per_page
            }
        }).then(() => {
            fetchCategoryProducts(1, ordering);
        });
    };

    const clearSearch = (createQueryFromFilters) => () => {
        categoryStore.clearSearchQuery();

        const query = createQueryFromFilters();
        const routeName = route.name;
        const params = {...route.params};

        router.push({
            name: routeName,
            params,
            query: {
                ...query,
                page: undefined,
                ordering: route.query.ordering !== '-id' ? route.query.ordering : undefined,
                per_page: route.query.per_page
            }
        }).then(() => {
            fetchCategoryProducts(1, route.query.ordering || '-id');
        });
    };

    provide('categoryPaginationHandlers', {
        handlePageChange,
        handleItemsPerPageChange
    });

    provide('categoryPaginationData', {
        currentPage: computed(() => currentPage.value),
        totalPages: computed(() => totalPages.value),
        hasItems: computed(() => hasItems.value),
        itemsPerPageOptions
    });

    const initialize = async () => {
        categoryStore.loadFiltersFromQuery(route.query);
        await fetchCategoryFilters();
        const page = parseInt(route.query.page) || 1;
        await fetchCategoryProducts(page, route.query.ordering || '-id');
    };

    const cleanup = () => {
        categoryStore.setAvailableFilters({gender: null, year: null});
    };

    return {
        isLoading,
        error,
        products,
        totalPages,
        totalItems,
        currentPage,
        itemsPerPageOptions,
        isLoadingFilters,
        filtersError,

        hasProducts,
        isEmpty,
        hasItems,
        masterCategoryId,
        subCategoryId,
        articleTypeId,

        availableFilters: computed(() => categoryStore.availableFilters),
        activeFilters: computed(() => categoryStore.activeFilters),
        searchQuery: computed(() => categoryStore.searchQuery),

        fetchProducts: fetchCategoryProducts,
        fetchCategoryProducts,
        fetchCategoryFilters,
        handlePageChange,
        handleItemsPerPageChange,
        handleOrderingChange,
        clearSearch,
        ensureValidPage,
        initialize,
        cleanup
    };
}
