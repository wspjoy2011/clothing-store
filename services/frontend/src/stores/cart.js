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
        totalPrice: (state) => state.cart?.total_price || 0,

        isAuthenticated: () => {
            const accountStore = useAccountStore()
            return accountStore.isAuthenticated
        },
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
