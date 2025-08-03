import { computed } from 'vue'

/**
 * Composable for cart UI-related logic and formatting
 * @param {Object} cartData - Cart data from useCart
 * @param {Ref} cartData.hasItems - Whether cart has items
 * @param {Ref} cartData.itemsCount - Number of items in cart
 * @param {Ref} cartData.totalPrice - Total price of cart
 * @returns {Object} UI helpers for cart display
 */
export function useCartUI(cartData) {
  const { hasItems, itemsCount, totalPrice } = cartData

  /**
   * Generate cart title for UI components
   */
  const cartTitle = computed(() => {
    return 'Shopping Cart'
  })

  /**
   * Generate cart tooltip text with item count and price
   */
  const cartTooltipText = computed(() => {
    if (!hasItems.value) {
      return 'Your cart is empty'
    }

    const itemText = itemsCount.value === 1 ? 'item' : 'items'
    const price = Number(totalPrice.value) || 0
    return `${itemsCount.value} ${itemText} • $${price.toFixed(2)}`
  })

  /**
   * Generate cart subtitle for mobile drawer and other components
   */
  const cartSubtitle = computed(() => {
    if (!hasItems.value) {
      return 'Empty'
    }

    const itemText = itemsCount.value === 1 ? 'item' : 'items'
    const price = Number(totalPrice.value) || 0
    return `${itemsCount.value} ${itemText} • $${price.toFixed(2)}`
  })

  /**
   * Generate formatted price string
   */
  const formattedTotalPrice = computed(() => {
    const price = Number(totalPrice.value) || 0
    return `$${price.toFixed(2)}`
  })

  /**
   * Generate item count text (e.g., "1 item", "3 items")
   */
  const itemCountText = computed(() => {
    if (!hasItems.value) return '0 items'

    const itemText = itemsCount.value === 1 ? 'item' : 'items'
    return `${itemsCount.value} ${itemText}`
  })

  return {
    cartTitle,
    cartTooltipText,
    cartSubtitle,
    formattedTotalPrice,
    itemCountText
  }
}
