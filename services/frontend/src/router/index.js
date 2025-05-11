import {createRouter, createWebHistory} from 'vue-router'

import HomePage from '@/views/HomePage.vue'
import CatalogPage from '@/views/CatalogPage.vue'

const routes = [
    {
        path: '/',
        name: 'home',
        component: HomePage
    },
    {
        path: '/catalog',
        name: 'catalog',
        component: CatalogPage
    }

]

const router = createRouter({
    history: createWebHistory(),
    routes
})

export default router
