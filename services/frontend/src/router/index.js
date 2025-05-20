import {createRouter, createWebHistory} from 'vue-router'
import { useUserPreferencesStore } from '@/stores/userPreferences'
import { useCatalogStore } from '@/stores/catalog'

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
            const catalogStore = useCatalogStore();

            const perPage = parseInt(route.query.per_page) || preferencesStore.itemsPerPage;

            if (route.query.per_page && parseInt(route.query.per_page) !== preferencesStore.itemsPerPage) {
                preferencesStore.setItemsPerPage(parseInt(route.query.per_page));
            }

            if (route.query.gender) {
                catalogStore.activeFilters.gender = route.query.gender;
            }

            if (route.query.min_year) {
                catalogStore.activeFilters.min_year = parseInt(route.query.min_year);
            }

            if (route.query.max_year) {
                catalogStore.activeFilters.max_year = parseInt(route.query.max_year);
            }

            if (route.query.q) {
                catalogStore.setSearchQuery(route.query.q);
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
