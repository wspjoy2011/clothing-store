import {ref, computed, watch} from 'vue';
import {useRouter} from 'vue-router';
import {useCatalogStore} from '@/stores/catalog';
import {useCategoryStore} from '@/stores/categoryStore';
import categoryService from '@/services/categoryService';


export function useCategoryProducts(route) {
    const router = useRouter();
    const catalogStore = useCatalogStore();
    const categoryStore = useCategoryStore();

    const isLoading = ref(true);
    const error = ref(null);
    const products = ref([]);
    const totalPages = ref(0);
    const totalItems = ref(0);
    const currentPage = ref(1);

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
            if (catalogStore.activeFilters.gender) filters.gender = catalogStore.activeFilters.gender;
            if (catalogStore.activeFilters.min_year) filters.min_year = catalogStore.activeFilters.min_year;
            if (catalogStore.activeFilters.max_year) filters.max_year = catalogStore.activeFilters.max_year;

            const result = await categoryService.getProductsByCategory(
                masterCategoryId.value,
                subCategoryId.value,
                articleTypeId.value,
                page,
                route.query.per_page || 12,
                ordering,
                filters,
                catalogStore.searchQuery
            );

            products.value = result.products;
            totalPages.value = result.total_pages;
            totalItems.value = result.total_items;
            currentPage.value = page;

            return result;
        } catch (err) {
            error.value = err;
            console.error('Error fetching category products:', err);
        } finally {
            isLoading.value = false;
        }
    };

    const handlePageChange = (page) => {
        const validPage = ensureValidPage(page);
        const query = createQueryFromFilters();

        const routeName = route.name;
        const params = {...route.params};

        router.push({
            name: routeName,
            params,
            query: {
                ...query,
                page: validPage > 1 ? validPage : undefined
            }
        });

        fetchCategoryProducts(validPage, route.query.ordering || '-id');
    };

    const handleItemsPerPageChange = (count) => {
        const query = createQueryFromFilters();
        const routeName = route.name;
        const params = {...route.params};

        router.push({
            name: routeName,
            params,
            query: {
                ...query,
                page: undefined,
                per_page: count
            }
        });

        fetchCategoryProducts(1, route.query.ordering || '-id');
    };

    const clearAllFilters = () => {
        catalogStore.clearFilters();

        const newQuery = {};
        if (route.query.ordering && route.query.ordering !== '-id') {
            newQuery.ordering = route.query.ordering;
        }
        if (route.query.per_page) {
            newQuery.per_page = route.query.per_page;
        }

        const routeName = route.name;
        const params = {...route.params};

        router.push({
            name: routeName,
            params,
            query: newQuery
        });

        fetchCategoryProducts(1, route.query.ordering || '-id');
    };

    const handleOrderingChange = (ordering) => {
        const query = createQueryFromFilters();
        const routeName = route.name;
        const params = {...route.params};

        router.push({
            name: routeName,
            params,
            query: {
                ...query,
                page: undefined,
                ordering: ordering !== '-id' ? ordering : undefined
            }
        });

        fetchCategoryProducts(1, ordering);
    };

    const clearSearch = () => {
        catalogStore.clearSearch();

        const query = {...route.query};
        delete query.q;
        delete query.page;

        const routeName = route.name;
        const params = {...route.params};

        router.push({
            name: routeName,
            params,
            query
        });

        fetchCategoryProducts(1, route.query.ordering || '-id');
    };

    watch(() => route.params, () => {
        fetchCategoryProducts(parseInt(route.query.page) || 1, route.query.ordering || '-id');
    }, {deep: true});

    watch(() => route.query, (newQuery, oldQuery) => {
        const filterParamsChanged =
            newQuery.gender !== oldQuery.gender ||
            newQuery.min_year !== oldQuery.min_year ||
            newQuery.max_year !== oldQuery.max_year ||
            newQuery.q !== oldQuery.q;

        const pageChanged = newQuery.page !== oldQuery.page;
        const orderingChanged = newQuery.ordering !== oldQuery.ordering;
        const perPageChanged = newQuery.per_page !== oldQuery.per_page;

        if (filterParamsChanged || pageChanged || orderingChanged || perPageChanged) {
            const page = parseInt(newQuery.page) || 1;
            const ordering = newQuery.ordering || '-id';

            fetchCategoryProducts(page, ordering);
        }
    }, {deep: true});

    const initialize = () => {
        catalogStore.loadFiltersFromQuery(route.query);

        fetchCategoryProducts(parseInt(route.query.page) || 1, route.query.ordering || '-id');
    };

    return {
        isLoading,
        error,
        products,
        totalPages,
        totalItems,
        currentPage,
        hasProducts,
        isEmpty,
        hasItems,
        itemsPerPageOptions,
        handlePageChange,
        handleItemsPerPageChange,
        clearAllFilters,
        handleOrderingChange,
        clearSearch,
        initialize
    };
}
