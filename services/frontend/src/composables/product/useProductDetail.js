import {ref, computed, onMounted, onUnmounted, watch} from 'vue';
import {useRouter} from 'vue-router';
import {useCatalogStore} from '@/stores/catalog';
import {useProductTitle} from './useProductTitle';

/**
 * Composable for product detail page logic
 * @param {Object} props - Component props
 * @returns {Object} - Product detail functionality
 */
export function useProductDetail(props) {
    const router = useRouter();
    const catalogStore = useCatalogStore();

    const imageLoading = ref(true);

    const product = computed(() => catalogStore.currentProduct);
    const isLoading = computed(() => catalogStore.productLoading);
    const error = computed(() => catalogStore.productError);
    const hasProduct = computed(() => !isLoading.value && !error.value && product.value);
    const showNotFound = computed(() => !isLoading.value && !error.value && !product.value);

    const {resetPageTitle} = useProductTitle(product);

    const breadcrumbItems = computed(() => [
        {
            title: 'Home',
            disabled: false,
            to: {name: 'home'}
        },
        {
            title: 'Catalog',
            disabled: false,
            to: {name: 'catalog'}
        },
        {
            title: product.value?.product_display_name || 'Product',
            disabled: true
        }
    ]);

    /**
     * Load product data
     */
    const loadProduct = async () => {
        try {
            if (props.productId) {
                await catalogStore.getProductById(props.productId);
                return;
            }

            const existingProductId = catalogStore.getProductIdBySlug(props.productSlug);
            if (existingProductId) {
                await catalogStore.getProductById(existingProductId);
                return;
            }

            await catalogStore.getProductBySlug(props.productSlug);
        } catch (error) {
            console.error('Error loading product:', error);
        }
    };

    /**
     * Handle image loading states
     */
    const handleImageLoaded = () => {
        imageLoading.value = false;
    };

    /**
     * Navigate back to previous page or catalog
     */
    const goBack = () => {
        if (window.history.length > 1) {
            router.go(-1);
        } else {
            router.push({name: 'catalog'});
        }
    };

    /**
     * Initialize component
     */
    const initialize = () => {
        catalogStore.clearCurrentProduct();
        loadProduct();
    };

    /**
     * Cleanup component
     */
    const cleanup = () => {
        catalogStore.clearCurrentProduct();
        resetPageTitle();
    };

    watch(() => props.productId, (newId) => {
        if (newId) {
            loadProduct();
        }
    }, {immediate: false});

    watch(() => props.productSlug, (newSlug) => {
        if (newSlug && !props.productId) {
            loadProduct();
        }
    }, {immediate: false});

    onMounted(initialize);
    onUnmounted(cleanup);

    return {
        // State
        product,
        isLoading,
        error,
        hasProduct,
        showNotFound,
        imageLoading,
        breadcrumbItems,

        // Actions
        goBack,
        handleImageLoaded,
        loadProduct
    };
}
