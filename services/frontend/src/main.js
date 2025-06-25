import {createApp} from 'vue'
import {createPinia} from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
import vue3GoogleLogin from 'vue3-google-login'

import App from '@/App.vue'
import router from '@/router'
import vuetify from '@/plugins/vuetify'
import {useAccountStore} from '@/stores/accounts'

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

accountStore.initializeAuth().then(() => {
    app.mount('#app')
}).catch((error) => {
    console.error('Failed to initialize authentication:', error)
    app.mount('#app')
})
