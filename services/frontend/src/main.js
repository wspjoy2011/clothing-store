import {createApp} from 'vue'
import {createPinia} from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
import vue3GoogleLogin from 'vue3-google-login'

import App from '@/App.vue'
import router from '@/router'
import vuetify from '@/plugins/vuetify'
import {useAccountStore} from '@/stores/accounts'
import {useCartStore} from '@/stores/cart'

const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)

const app = createApp(App)

app.use(pinia)
app.use(router)
app.use(vuetify)

app.use(vue3GoogleLogin, {
    clientId: import.meta.env.VITE_GOOGLE_CLIENT_ID
})

const accountStore = useAccountStore()
const cartStore = useCartStore()

let wasAuthenticated = accountStore.isAuthenticated

const handleAuthChange = async () => {
    const isNowAuthenticated = accountStore.isAuthenticated

    if (!wasAuthenticated && isNowAuthenticated) {
        console.log('User logged in, switching to user cart')
        try {
            await cartStore.switchToUserCart()
        } catch (error) {
            console.error('Failed to switch to user cart:', error)
        }
    }

    else if (wasAuthenticated && !isNowAuthenticated) {
        console.log('User logged out, switching to anonymous cart')
        try {
            await cartStore.switchToAnonymousCart()
        } catch (error) {
            console.error('Failed to switch to anonymous cart:', error)
        }
    }

    wasAuthenticated = isNowAuthenticated
}

router.afterEach(async () => {
    await handleAuthChange()
})

accountStore.initializeAuth().then(async () => {
    await cartStore.initializeCart()

    wasAuthenticated = accountStore.isAuthenticated

    app.mount('#app')
}).catch(async (error) => {
    console.error('Failed to initialize authentication:', error)

    try {
        await cartStore.initializeCart()
        wasAuthenticated = accountStore.isAuthenticated
    } catch (cartError) {
        console.error('Failed to initialize cart:', cartError)
    }

    app.mount('#app')
})
