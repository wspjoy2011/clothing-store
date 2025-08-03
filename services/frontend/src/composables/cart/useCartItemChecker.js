import { computed } from 'vue'
import { useCartStore } from '@/stores/cart.js'

/**
 * Composable for checking cart items and their status
 * Provides reactive methods to check if products are in cart and get their details
 *
 * @returns {Object} Cart item checking utilities
 */
export function useCartItemChecker() {
  const cartStore = useCartStore()

  /**
   * Check if a specific product is in cart
   * @param {number} productId - Product ID to check
   * @returns {ComputedRef<boolean>} - Reactive boolean indicating if product is in cart
   */
  const isProductInCart = (productId) => {
    return computed(() => cartStore.isProductInCart(productId))
  }

  /**
   * Get cart item information for specific product
   * @param {number} productId - Product ID to get info for
   * @returns {ComputedRef<Object|null>} - Reactive cart item object or null
   */
  const getCartItemInfo = (productId) => {
    return computed(() => cartStore.getCartItemByProductId(productId))
  }

  /**
   * Get quantity of specific product in cart
   * @param {number} productId - Product ID to get quantity for
   * @returns {ComputedRef<number>} - Reactive quantity in cart (0 if not in cart)
   */
  const getProductQuantity = (productId) => {
    return computed(() => cartStore.getProductQuantityInCart(productId))
  }

  /**
   * Get all product IDs that are currently in cart
   * @returns {ComputedRef<Array<number>>} - Reactive array of product IDs
   */
  const cartProductIds = computed(() => cartStore.cartProductIds)

  /**
   * Get cart items as a Map for efficient lookups
   * @returns {ComputedRef<Map<number, Object>>} - Reactive Map of product_id to cart item
   */
  const cartItemsMap = computed(() => cartStore.cartItemsMap)

  /**
   * Check multiple products at once
   * @param {Array<number>} productIds - Array of product IDs to check
   * @returns {ComputedRef<Object>} - Reactive object with productId as key and boolean as value
   */
  const checkMultipleProducts = (productIds) => {
    return computed(() => {
      const results = {}
      productIds.forEach(productId => {
        results[productId] = cartStore.isProductInCart(productId)
      })
      return results
    })
  }

  /**
   * Get formatted cart item display info
   * @param {number} productId - Product ID to get display info for
   * @returns {ComputedRef<Object>} - Reactive object with display information
   */
  const getCartItemDisplayInfo = (productId) => {
    return computed(() => {
      const item = cartStore.getCartItemByProductId(productId)

      if (!item) {
        return {
          isInCart: false,
          quantity: 0,
          displayText: '',
          badgeText: '',
          tooltipText: 'Add to cart'
        }
      }

      const quantity = item.quantity
      const itemText = quantity === 1 ? 'item' : 'items'
      const price = Number(item.unit_price) || 0
      const totalPrice = price * quantity

      return {
        isInCart: true,
        quantity: quantity,
        displayText: `${quantity} in cart`,
        badgeText: quantity.toString(),
        tooltipText: `${quantity} ${itemText} • $${totalPrice.toFixed(2)}`,
        unitPrice: price,
        totalPrice: totalPrice,
        salePrice: item.sale_price ? Number(item.sale_price) : null
      }
    })
  }

  /**
   * Check if cart has any items
   * @returns {ComputedRef<boolean>} - Reactive boolean indicating if cart has items
   */
  const hasCartItems = computed(() => cartStore.hasItems)

  /**
   * Get total number of items in cart
   * @returns {ComputedRef<number>} - Reactive total item count
   */
  const totalItemsCount = computed(() => cartStore.itemsCount)

  /**
   * Non-reactive method to directly check if product is in cart
   * Useful for one-time checks or in async functions
   * @param {number} productId - Product ID to check
   * @returns {boolean} - True if product is in cart
   */
  const checkProductInCartSync = (productId) => {
    return cartStore.checkProductInCart(productId)
  }

  /**
   * Non-reactive method to get cart item info
   * @param {number} productId - Product ID to get info for
   * @returns {Object|null} - Cart item object or null
   */
  const getCartItemInfoSync = (productId) => {
    return cartStore.getCartItemInfo(productId)
  }

  /**
   * Non-reactive method to get product quantity
   * @param {number} productId - Product ID to get quantity for
   * @returns {number} - Quantity in cart
   */
  const getProductQuantitySync = (productId) => {
    return cartStore.getProductQuantity(productId)
  }

  return {
    // Reactive computed methods (for templates and watchers)
    isProductInCart,
    getCartItemInfo,
    getProductQuantity,
    getCartItemDisplayInfo,
    checkMultipleProducts,

    // Reactive computed properties
    cartProductIds,
    cartItemsMap,
    hasCartItems,
    totalItemsCount,

    // Synchronous methods (for imperative usage)
    checkProductInCartSync,
    getCartItemInfoSync,
    getProductQuantitySync
  }
}
