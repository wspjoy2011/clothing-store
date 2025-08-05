import {computed, onMounted} from 'vue'
import {useTheme} from 'vuetify'
import {useCartState} from '@/composables/cart/useCartState.js'
import {useCartActions} from '@/composables/cart/useCartActions.js'
import {useCartErrorHandler} from '@/composables/cart/useCartErrorHandler.js'
import {useCartFormatting} from '@/composables/cart/useCartFormatting.js'
import {usePageTitle} from '@/composables/usePageTitle.js'

export function useCartPage(options = {}) {
    const {
        autoInitialize = true,
        showNotifications = true
    } = options

    const theme = useTheme()
    const isDarkTheme = computed(() => theme.global.current.value.dark)

    usePageTitle('StyleShop - Shopping Cart')

    const {
        isAddingItem,
        addItemError,
        isRemovingItem,
        removeItemError,

        cart,
        isLoading,
        error,
        hasItems,
        itemsCount,
        totalPrice,
        isAuthenticated,
        isInitialized,

        clearAddItemError,
        setAddingItem,
        setAddItemError,
        clearRemoveItemError,
        setRemovingItem,
        setRemoveItemError
    } = useCartState()

    const {
        initializeCart,
        createAddItemHandler,
        createRemoveItemHandler,
        reloadCart,
        switchToUserCart,
        switchToAnonymousCart
    } = useCartActions()

    const {
        getAddItemErrorDetails,
        getCartErrorDetails
    } = useCartErrorHandler()

    const {
        formattedTotalAmount,
        formattedTotalDiscount,
        formattedFinalAmount,
        hasDiscount,

        parsePrice,
        formatItemPrice,
        formatItemTotal,
        formatItemSaleTotal,
        getItemDiscount,
        hasItemDiscount
    } = useCartFormatting(cart)

    const addItemToCart = createAddItemHandler({
        isAddingItem,
        setAddingItem,
        clearAddItemError,
        setAddItemError
    });

    const removeItemFromCart = createRemoveItemHandler({
        isRemovingItem,
        setRemovingItem,
        clearRemoveItemError,
        setRemoveItemError
    });

    if (autoInitialize) {
        onMounted(async () => {
            if (!isInitialized.value) {
                await initializeCart()
            }
        })
    }

    return {
        // Theme
        isDarkTheme,

        // State
        cart,
        isLoading,
        error,
        hasItems,
        itemsCount,
        totalPrice,
        isAuthenticated,
        isInitialized,

        // Add item state
        isAddingItem,
        addItemError,

        // Remove item state
        isRemovingItem,
        removeItemError,

        // Actions
        initializeCart,
        addItemToCart: (itemData) => addItemToCart(itemData, showNotifications),
        removeItemFromCart: (itemId) => removeItemFromCart(itemId, showNotifications),
        reloadCart,
        switchToUserCart,
        switchToAnonymousCart,
        clearAddItemError,
        clearRemoveItemError,

        // Error handling
        getAddItemErrorDetails,
        getCartErrorDetails,

        // Price formatting and calculations
        formattedTotalAmount,
        formattedTotalDiscount,
        formattedFinalAmount,
        hasDiscount,
        parsePrice,
        formatItemPrice,
        formatItemTotal,
        formatItemSaleTotal,
        getItemDiscount,
        hasItemDiscount
    }
}
