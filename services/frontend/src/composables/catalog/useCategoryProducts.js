import {ref, computed, provide, watch, onMounted, onBeforeUnmount} from 'vue'
import {useRouter} from 'vue-router'
import {useCategoryStore} from '@/stores/categoryStore'

export function useCategoryProducts(route) {
    const router = useRouter()
    const categoryStore = useCategoryStore()

    const isLoadingFilters = ref(false)
    const filtersError = ref(null)

    const masterCategoryId = computed(() => {
        const slug = route.params.masterCategory
        return slug ? categoryStore.getMasterCategoryIdBySlug(slug) : null
    })

    const subCategoryId = computed(() => {
        if (!masterCategoryId.value || !route.params.subCategory) return null
        return categoryStore.getSubCategoryIdBySlug(masterCategoryId.value, route.params.subCategory)
    })

    const articleTypeId = computed(() => {
        if (!masterCategoryId.value || !subCategoryId.value || !route.params.articleType) return null
        return categoryStore.getArticleTypeIdBySlug(
            masterCategoryId.value,
            subCategoryId.value,
            route.params.articleType
        )
    })

    const itemsPerPageOptions = [8, 12, 16, 20]

    const hasProducts = computed(
        () => !categoryStore.loading && !categoryStore.error && categoryStore.products.length > 0
    )

    const isEmpty = computed(
        () => !categoryStore.loading && !categoryStore.error && categoryStore.products.length === 0
    )

    const hasItems = computed(
        () => !categoryStore.loading && !categoryStore.error && categoryStore.totalPages > 0
    )

    const ensureValidPage = (page) => {
        if (categoryStore.totalPages > 0 && page > categoryStore.totalPages) {
            return categoryStore.totalPages
        }
        return page
    }

    const filtersRequestSeq = ref(0)
    let isUnmounted = false

    const fetchCategoryProducts = async (page = 1, ordering = '-id') => {
        if (!masterCategoryId.value) return
        await categoryStore.fetchProducts(
            page,
            ordering,
            masterCategoryId.value,
            subCategoryId.value,
            articleTypeId.value
        )
    }

    const resetAvailableFilters = () => {
        categoryStore.setAvailableFilters({
            gender: null,
            year: null,
            price: null,
            is_available: null
        })
    }

    const fetchCategoryFilters = async () => {
        if (!masterCategoryId.value) {
            resetAvailableFilters()
            return
        }

        const mySeq = ++filtersRequestSeq.value

        resetAvailableFilters()

        isLoadingFilters.value = true
        filtersError.value = null

        try {
            await categoryStore.fetchCategoryFilters(
                masterCategoryId.value,
                subCategoryId.value,
                articleTypeId.value
            )
        } catch (err) {
            if (mySeq === filtersRequestSeq.value) {
                filtersError.value = err
            }
        } finally {
            if (mySeq === filtersRequestSeq.value) {
                isLoadingFilters.value = false
            }
        }
    }

    const handlePageChange =
        (createQueryFromFilters) =>
            (page) => {
                const validPage = ensureValidPage(page)
                const query = createQueryFromFilters()

                const routeName = route.name
                const params = {...route.params}

                router
                    .push({
                        name: routeName,
                        params,
                        query: {
                            ...query,
                            page: validPage > 1 ? validPage : undefined,
                            ordering: route.query.ordering !== '-id' ? route.query.ordering : undefined,
                            per_page: route.query.per_page
                        }
                    })
                    .then(() => {
                        return fetchCategoryProducts(validPage, route.query.ordering || '-id')
                    })
            }

    const handleItemsPerPageChange =
        (createQueryFromFilters) =>
            (count) => {
                const query = createQueryFromFilters()
                const routeName = route.name
                const params = {...route.params}

                router
                    .push({
                        name: routeName,
                        params,
                        query: {
                            ...query,
                            page: undefined,
                            per_page: count,
                            ordering: route.query.ordering !== '-id' ? route.query.ordering : undefined
                        }
                    })
                    .then(() => {
                        return fetchCategoryProducts(1, route.query.ordering || '-id')
                    })
            }

    const handleOrderingChange =
        (createQueryFromFilters) =>
            (ordering) => {
                const query = createQueryFromFilters()
                const routeName = route.name
                const params = {...route.params}

                router
                    .push({
                        name: routeName,
                        params,
                        query: {
                            ...query,
                            page: undefined,
                            ordering: ordering !== '-id' ? ordering : undefined,
                            per_page: route.query.per_page
                        }
                    })
                    .then(() => {
                        return fetchCategoryProducts(1, ordering)
                    })
            }

    const clearSearch =
        (createQueryFromFilters) =>
            () => {
                categoryStore.clearSearchQuery()

                const query = createQueryFromFilters()
                const routeName = route.name
                const params = {...route.params}

                router
                    .push({
                        name: routeName,
                        params,
                        query: {
                            ...query,
                            page: undefined,
                            ordering: route.query.ordering !== '-id' ? route.query.ordering : undefined,
                            per_page: route.query.per_page
                        }
                    })
                    .then(() => {
                        return fetchCategoryProducts(1, route.query.ordering || '-id')
                    })
            }

    provide('categoryPaginationHandlers', {
        handlePageChange,
        handleItemsPerPageChange
    })

    provide('categoryPaginationData', {
        currentPage: computed(() => categoryStore.currentPage),
        totalPages: computed(() => categoryStore.totalPages),
        hasItems: computed(() => hasItems.value),
        itemsPerPageOptions
    })

    const initialize = async () => {
        categoryStore.loadFiltersFromQuery(route.query)
        await fetchCategoryFilters()
        const page = parseInt(route.query.page) || 1
        await fetchCategoryProducts(page, route.query.ordering || '-id')
    }

    const cleanup = () => {
        resetAvailableFilters()
    }

    watch([masterCategoryId, subCategoryId, articleTypeId], async () => {
        if (isUnmounted) return
        await fetchCategoryFilters()
        const ordering = route.query.ordering || '-id'
        const page = parseInt(route.query.page) || 1
        await fetchCategoryProducts(page, ordering)
    })

    onMounted(() => {
        void initialize()
    })

    onBeforeUnmount(() => {
        isUnmounted = true
        cleanup()
    })

    return {
        // Store data proxies
        isLoading: computed(() => categoryStore.loading),
        error: computed(() => categoryStore.error),
        products: computed(() => categoryStore.products),
        totalPages: computed(() => categoryStore.totalPages),
        totalItems: computed(() => categoryStore.totalItems),
        currentPage: computed(() => categoryStore.currentPage),

        // Local loading states
        itemsPerPageOptions,
        isLoadingFilters,
        filtersError,

        // Computed states
        hasProducts,
        isEmpty,
        hasItems,
        masterCategoryId,
        subCategoryId,
        articleTypeId,

        // Store getters
        availableFilters: computed(() => categoryStore.availableFilters),
        activeFilters: computed(() => categoryStore.activeFilters),
        searchQuery: computed(() => categoryStore.searchQuery),

        // Methods
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
    }
}
