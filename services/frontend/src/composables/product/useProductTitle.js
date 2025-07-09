import {watch} from 'vue';

/**
 * Composable for managing product page title
 * @param {Object} product - Reactive product object
 * @returns {Object} - Title management functions
 */
export function useProductTitle(product) {
    /**
     * Update page title based on product data
     */
    const updatePageTitle = () => {
        if (product.value?.product_display_name) {
            document.title = `StyleShop - ${product.value.product_display_name}`;
        } else {
            document.title = 'StyleShop - Product';
        }
    };

    /**
     * Reset page title to default
     */
    const resetPageTitle = () => {
        document.title = 'StyleShop';
    };

    watch(product, updatePageTitle, {immediate: true});

    return {
        updatePageTitle,
        resetPageTitle
    };
}
