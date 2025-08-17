import {defineStore} from 'pinia'
import cartService from '@/services/cartService.js'
import {useAccountStore} from '@/stores/accounts.js'

export const useCartStore = defineStore('cart', {
    state: () => ({
        cart: null,
        cartToken: null,

        isLoading: false,
        error: null,

        isInitialized: false,
    }),

    getters: {
        hasItems: (state) => state.cart?.items?.length > 0,
        itemsCount: (state) => state.cart?.items?.reduce((sum, item) => sum + item.quantity, 0) || 0,
        totalPrice: (state) => state.cart?.final_amount || 0,

        isAuthenticated: () => {
            const accountStore = useAccountStore()
            return accountStore.isAuthenticated
        },

        /**
         * Get all cart items as a Map for fast lookup by product_id
         * @returns {Map<number, Object>} Map of product_id to cart item
         */
        cartItemsMap: (state) => {
            if (!state.cart?.items) {
                return new Map()
            }

            const itemsMap = new Map()
            state.cart.items.forEach(item => {
                itemsMap.set(item.product_id, item)
            })
            return itemsMap
        },

        /**
         * Check if product is in cart
         * @returns {Function} Function that takes product_id and returns boolean
         */
        isProductInCart: (state) => (productId) => {
            if (!state.cart?.items) {
                return false
            }

            return state.cart.items.some(item => item.product_id === productId)
        },

        /**
         * Get cart item by product ID
         * @returns {Function} Function that takes product_id and returns cart item or null
         */
        getCartItemByProductId: (state) => (productId) => {
            if (!state.cart?.items) {
                return null
            }

            return state.cart.items.find(item => item.product_id === productId) || null
        },

        /**
         * Get quantity of specific product in cart
         * @returns {Function} Function that takes product_id and returns quantity
         */
        getProductQuantityInCart: (state) => (productId) => {
            const item = state.cart?.items?.find(item => item.product_id === productId)
            return item ? item.quantity : 0
        },

        /**
         * Get all product IDs that are in cart
         * @returns {Array<number>} Array of product IDs in cart
         */
        cartProductIds: (state) => {
            if (!state.cart?.items) {
                return []
            }

            return state.cart.items.map(item => item.product_id)
        }
    },

    actions: {
        async initializeCart() {
            if (this.isInitialized) {
                return
            }

            this.isLoading = true
            this.error = null

            try {
                if (this.isAuthenticated) {
                    await this.loadUserCart()
                } else {
                    await this.loadAnonymousCart()
                }
            } catch (error) {
                this.error = error.message
                console.error('Failed to initialize cart:', error)

                if (error.status === 401 && this.isAuthenticated === false) {
                    try {
                        await this.loadAnonymousCart()
                        this.error = null
                    } catch (anonymousError) {
                        console.error('Failed to create anonymous cart after logout:', anonymousError)
                    }
                }
            } finally {
                this.isLoading = false
                this.isInitialized = true
            }
        },

        async loadUserCart() {
            this.cart = await cartService.getCart()
        },

        async loadAnonymousCart() {
            if (!this.cartToken) {
                await this.createCartToken()
            }

            this.cart = await cartService.getCartByToken(this.cartToken)
        },

        async createCartToken() {
            const response = await cartService.createCartToken()
            this.cartToken = response.token
        },

        /**
         * Universal method to add item to cart
         * Automatically chooses between authenticated and anonymous methods
         * @param {Object} itemData - Item data {product_id, quantity}
         * @returns {Promise<Object>} - Added cart item
         */
        async addItemToCart(itemData) {
            this.isLoading = true
            this.error = null

            try {
                let result

                if (this.isAuthenticated) {
                    result = await this.addItemToUserCart(itemData)
                } else {
                    result = await this.addItemToAnonymousCart(itemData)
                }

                await this.reloadCart()

                return result
            } catch (error) {
                this.error = error.message
                console.error('Failed to add item to cart:', error)
                throw error
            } finally {
                this.isLoading = false
            }
        },

        /**
         * Add item to cart for authenticated user
         * @param {Object} itemData - Item data {product_id, quantity}
         * @returns {Promise<Object>} - Added cart item
         */
        async addItemToUserCart(itemData) {
            return await cartService.addItemToCart(itemData)
        },

        /**
         * Add item to cart for anonymous user
         * @param {Object} itemData - Item data {product_id, quantity}
         * @returns {Promise<Object>} - Added cart item
         */
        async addItemToAnonymousCart(itemData) {
            if (!this.cartToken) {
                await this.createCartToken()
            }

            return await cartService.addItemToCartByToken(this.cartToken, itemData)
        },

        /**
         * Universal method to remove item from cart
         * Automatically chooses between authenticated and anonymous methods
         * @param {number} itemId - Cart item ID to remove
         * @returns {Promise<void>}
         */
        async removeItemFromCart(itemId) {
            this.isLoading = true
            this.error = null

            try {
                if (this.isAuthenticated) {
                    await this.removeItemFromUserCart(itemId)
                } else {
                    await this.removeItemFromAnonymousCart(itemId)
                }

                await this.reloadCart()
            } catch (error) {
                this.error = error.message
                console.error('Failed to remove item from cart:', error)
                throw error
            } finally {
                this.isLoading = false
            }
        },

        /**
         * Remove item from cart for authenticated user
         * @param {number} itemId - Cart item ID to remove
         * @returns {Promise<void>}
         */
        async removeItemFromUserCart(itemId) {
            return await cartService.removeItemFromCart(itemId)
        },

        /**
         * Remove item from cart for anonymous user
         * @param {number} itemId - Cart item ID to remove
         * @returns {Promise<void>}
         */
        async removeItemFromAnonymousCart(itemId) {
            if (!this.cartToken) {
                await this.createCartToken()
            }

            return await cartService.removeItemFromCartByToken(this.cartToken, itemId)
        },

        /**
         * Universal method to update item quantity in cart
         * Automatically chooses between authenticated and anonymous methods
         * @param {number} itemId - Cart item ID to update
         * @param {Object} itemData - Update payload { quantity }
         * @returns {Promise<Object>} - Updated cart item
         */
        async updateItemInCart(itemId, itemData) {
            this.isLoading = true
            this.error = null

            try {
                let result

                if (this.isAuthenticated) {
                    result = await this.updateItemInUserCart(itemId, itemData)
                } else {
                    result = await this.updateItemInAnonymousCart(itemId, itemData)
                }

                await this.reloadCart()

                return result
            } catch (error) {
                this.error = error.message
                throw error
            } finally {
                this.isLoading = false
            }
        },

        /**
         * Update item quantity for authenticated user
         * @param {number} itemId - Cart item ID to update
         * @param {Object} itemData - Update payload { quantity }
         * @returns {Promise<Object>} - Updated cart item
         */
        async updateItemInUserCart(itemId, itemData) {
            return await cartService.updateItemInCart(itemId, itemData)
        },

        /**
         * Update item quantity for anonymous user
         * @param {number} itemId - Cart item ID to update
         * @param {Object} itemData - Update payload { quantity }
         * @returns {Promise<Object>} - Updated cart item
         */
        async updateItemInAnonymousCart(itemId, itemData) {
            if (!this.cartToken) {
                await this.createCartToken()
            }

            return await cartService.updateItemInCartByToken(this.cartToken, itemId, itemData)
        },

        /**
         * Reload cart data from server
         */
        async reloadCart() {
            if (this.isAuthenticated) {
                await this.loadUserCart()
            } else {
                await this.loadAnonymousCart()
            }
        },

        /**
         * Check if specific product is in cart
         * @param {number} productId - Product ID to check
         * @returns {boolean} - True if product is in cart
         */
        checkProductInCart(productId) {
            return this.isProductInCart(productId)
        },

        /**
         * Get cart item information for specific product
         * @param {number} productId - Product ID to get info for
         * @returns {Object|null} - Cart item object or null if not found
         */
        getCartItemInfo(productId) {
            return this.getCartItemByProductId(productId)
        },

        /**
         * Get quantity of specific product in cart
         * @param {number} productId - Product ID to get quantity for
         * @returns {number} - Quantity in cart (0 if not in cart)
         */
        getProductQuantity(productId) {
            return this.getProductQuantityInCart(productId)
        },

        /**
         * Check if multiple products are in cart
         * @param {Array<number>} productIds - Array of product IDs to check
         * @returns {Object} - Object with productId as key and boolean as value
         */
        checkMultipleProductsInCart(productIds) {
            const results = {}
            productIds.forEach(productId => {
                results[productId] = this.isProductInCart(productId)
            })
            return results
        },

        resetInitialization() {
            this.isInitialized = false
            this.cart = null
            this.error = null
        },

        async switchToAnonymousCart() {
            this.resetInitialization()
            this.cartToken = null
            await this.initializeCart()
        },

        async switchToUserCart() {
            console.log('Switching to user cart after login')

            this.isLoading = true
            this.error = null

            try {
                await this.loadUserCart()
                console.log('Successfully switched to user cart')
            } catch (error) {
                this.error = error.message
                console.error('Failed to switch to user cart:', error)
                throw error
            } finally {
                this.isLoading = false
            }
        }
    },

    persist: [
        {
            key: 'cart-tokens',
            storage: localStorage,
            paths: ['cartToken']
        }
    ]
})
