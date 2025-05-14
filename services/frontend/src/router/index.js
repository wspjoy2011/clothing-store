import {createRouter, createWebHistory} from 'vue-router'
import { useUserPreferencesStore } from '@/stores/userPreferences'

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
        component: CatalogPage,
        props: route => {
            const preferencesStore = useUserPreferencesStore();
            
            const perPage = parseInt(route.query.per_page) || preferencesStore.itemsPerPage;
            
            if (route.query.per_page && parseInt(route.query.per_page) !== preferencesStore.itemsPerPage) {
                preferencesStore.setItemsPerPage(parseInt(route.query.per_page));
            }
            
            return {
                page: parseInt(route.query.page) || 1,
                perPage,
                ordering: route.query.ordering || '-id'
            }
        }
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

export default router
