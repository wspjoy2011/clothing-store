import {computed} from 'vue';

/**
 * Composable for product inventory logic
 * Handles availability, discounts, pricing, and stock management
 *
 * @param {Object} product - Product object with inventory data
 * @returns {Object} - Inventory-related computed properties and methods
 */
export function useProductInventory(product) {
    /**
     * Check if product is available for purchase
     */
    const isAvailable = computed(() =>
        product.value?.inventory?.is_in_stock && product.value?.inventory?.is_active
    );

    /**
     * Check if product has a discount (sale_price < base_price)
     */
    const hasDiscount = computed(() => {
        const inventory = product.value?.inventory;
        if (!inventory?.sale_price || !inventory?.base_price) {
            return false;
        }
        return parseFloat(inventory.sale_price) < parseFloat(inventory.base_price);
    });

    /**
     * Get the effective price (sale_price if on discount, otherwise base_price)
     */
    const effectivePrice = computed(() => {
        const inventory = product.value?.inventory;
        if (!inventory) return null;

        return hasDiscount.value ? inventory.sale_price : inventory.base_price;
    });

    /**
     * Get discount percentage
     */
    const discountPercentage = computed(() => {
        if (!hasDiscount.value) return 0;

        const inventory = product.value?.inventory;
        const basePrice = parseFloat(inventory.base_price);
        const salePrice = parseFloat(inventory.sale_price);

        return Math.round(((basePrice - salePrice) / basePrice) * 100);
    });

    /**
     * Get available quantity
     */
    const availableQuantity = computed(() =>
        product.value?.inventory?.available_quantity || 0
    );

    /**
     * Get stock status text
     */
    const stockText = computed(() => {
        const inventory = product.value?.inventory;
        if (!inventory) return 'N/A';

        const availableQty = inventory.available_quantity;

        if (!inventory.is_active || !inventory.is_in_stock || availableQty <= 0) {
            return 'Out of Stock';
        }

        if (availableQty <= 5) {
            return `${availableQty} left`;
        }

        return 'In Stock';
    });

    /**
     * Get stock status color for UI components
     */
    const stockColor = computed(() => {
        const inventory = product.value?.inventory;
        if (!inventory) return 'grey';

        const availableQty = inventory.available_quantity;

        if (!inventory.is_active || !inventory.is_in_stock || availableQty <= 0) {
            return 'error';
        } else if (availableQty <= 5) {
            return 'warning';
        } else {
            return 'success';
        }
    });

    /**
     * Check if stock is low (5 or fewer items)
     */
    const isLowStock = computed(() => {
        const availableQty = availableQuantity.value;
        return availableQty > 0 && availableQty <= 5;
    });

    /**
     * Check if product is out of stock
     */
    const isOutOfStock = computed(() => {
        return !isAvailable.value || availableQuantity.value <= 0;
    });

    /**
     * Get formatted price string
     */
    const getFormattedPrice = (price) => {
        const inventory = product.value?.inventory;
        if (!inventory || !price) return '';

        return `${price} ${inventory.currency}`;
    };

    /**
     * Get base price formatted
     */
    const formattedBasePrice = computed(() =>
        getFormattedPrice(product.value?.inventory?.base_price)
    );

    /**
     * Get sale price formatted
     */
    const formattedSalePrice = computed(() =>
        getFormattedPrice(product.value?.inventory?.sale_price)
    );

    /**
     * Get effective price formatted
     */
    const formattedEffectivePrice = computed(() =>
        getFormattedPrice(effectivePrice.value)
    );

    /**
     * Check if add to cart action is allowed
     */
    const canAddToCart = computed(() =>
        isAvailable.value && !isOutOfStock.value
    );

    /**
     * Get button text based on availability
     */
    const getActionButtonText = (defaultText = 'Add to Cart') => {
        if (isOutOfStock.value) return 'Out of Stock';
        if (!isAvailable.value) return 'Unavailable';
        return defaultText;
    };

    /**
     * Get button color based on availability
     */
    const getActionButtonColor = (defaultColor = 'primary') => {
        return isAvailable.value ? defaultColor : 'grey';
    };

    return {
        // Availability
        isAvailable,
        isOutOfStock,
        canAddToCart,

        // Discounts
        hasDiscount,
        discountPercentage,

        // Pricing
        effectivePrice,
        formattedBasePrice,
        formattedSalePrice,
        formattedEffectivePrice,
        getFormattedPrice,

        // Stock
        availableQuantity,
        stockText,
        stockColor,
        isLowStock,

        // UI Helpers
        getActionButtonText,
        getActionButtonColor
    };
}
