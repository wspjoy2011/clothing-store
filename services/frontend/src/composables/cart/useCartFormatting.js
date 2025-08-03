import { computed } from 'vue'

/**
 * Composable for cart price calculations and formatting
 */
export function useCartFormatting(cart) {
    /**
     * Helper function to safely parse price values
     * @param {string|number|null|undefined} price
     * @returns {number}
     */
    const parsePrice = (price) => {
        if (price === null || price === undefined) return 0
        return typeof price === 'string' ? parseFloat(price) : price
    }

    /**
     * Calculate discount for a single cart item
     * @param {Object} item - Cart item
     * @returns {number} - Item discount amount
     */
    const calculateItemDiscount = (item) => {
        if (!item.sale_price) return 0

        const unitPrice = parsePrice(item.unit_price)
        const salePrice = parsePrice(item.sale_price)
        const quantity = item.quantity || 1

        if (salePrice >= unitPrice) return 0

        return (unitPrice - salePrice) * quantity
    }

    /**
     * Calculate total discount from all cart items with sale prices
     * @returns {number} - Total calculated discount
     */
    const calculatedTotalDiscount = computed(() => {
        if (!cart.value?.items) return 0

        return cart.value.items.reduce((total, item) => {
            return total + calculateItemDiscount(item)
        }, 0)
    })

    /**
     * Calculate subtotal from all cart items (using unit prices * quantity)
     * @returns {number} - Calculated subtotal
     */
    const calculatedSubtotal = computed(() => {
        if (!cart.value?.items) return 0

        return cart.value.items.reduce((total, item) => {
            const unitPrice = parsePrice(item.unit_price)
            const quantity = item.quantity || 1
            return total + (unitPrice * quantity)
        }, 0)
    })

    /**
     * Calculate final amount (subtotal - discount)
     * @returns {number} - Calculated final amount
     */
    const calculatedFinalAmount = computed(() => {
        return calculatedSubtotal.value - calculatedTotalDiscount.value
    })

    const formattedTotalAmount = computed(() => {
        return calculatedSubtotal.value.toFixed(2)
    })

    const formattedTotalDiscount = computed(() => {
        return calculatedTotalDiscount.value.toFixed(2)
    })

    const formattedFinalAmount = computed(() => {
        return calculatedFinalAmount.value.toFixed(2)
    })

    const hasDiscount = computed(() => {
        return calculatedTotalDiscount.value > 0
    })

    const formatItemPrice = (price) => {
        return parsePrice(price).toFixed(2)
    }

    const formatItemTotal = (item) => {
        const unitPrice = parsePrice(item.unit_price)
        const quantity = item.quantity || 1
        return (unitPrice * quantity).toFixed(2)
    }

    const formatItemSaleTotal = (item) => {
        if (!item.sale_price) return formatItemTotal(item)

        const salePrice = parsePrice(item.sale_price)
        const quantity = item.quantity || 1
        return (salePrice * quantity).toFixed(2)
    }

    const getItemDiscount = (item) => {
        return calculateItemDiscount(item).toFixed(2)
    }

    const hasItemDiscount = (item) => {
        return calculateItemDiscount(item) > 0
    }

    return {
        // Price calculation utilities
        parsePrice,
        calculateItemDiscount,

        // Computed cart totals
        calculatedSubtotal,
        calculatedTotalDiscount,
        calculatedFinalAmount,

        // Formatted display values
        formattedTotalAmount,
        formattedTotalDiscount,
        formattedFinalAmount,
        hasDiscount,

        // Item formatting helpers
        formatItemPrice,
        formatItemTotal,
        formatItemSaleTotal,
        getItemDiscount,
        hasItemDiscount
    }
}
