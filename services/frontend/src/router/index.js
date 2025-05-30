import {createRouter, createWebHistory} from 'vue-router'
import { useUserPreferencesStore } from '@/stores/userPreferences'
import { useCatalogStore } from '@/stores/catalog'

import HomePage from '@/views/HomePage.vue'
import CatalogPage from '@/views/CatalogPage.vue'
import CategoryPage from '@/views/CategoryPage.vue'

const processCatalogRouteProps = (route) => {
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
};

const processCategoryRouteProps = (route) => {
    return {
        masterCategoryId: route.params.masterCategoryId,
        subCategoryId: route.params.subCategoryId,
        articleTypeId: route.params.articleTypeId
    }
};

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
        props: processCatalogRouteProps
    },
    {
        path: '/category/:masterCategoryId',
        name: 'master-category',
        component: CategoryPage,
        props: processCategoryRouteProps
    },
    {
        path: '/category/:masterCategoryId/:subCategoryId',
        name: 'sub-category',
        component: CategoryPage,
        props: processCategoryRouteProps
    },
    {
        path: '/category/:masterCategoryId/:subCategoryId/:articleTypeId',
        name: 'article-type',
        component: CategoryPage,
        props: processCategoryRouteProps
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes,
    scrollBehavior(to, from, savedPosition) {
        if (savedPosition) {
            return savedPosition;
        }
        return {top: 0};
    }
})

router.beforeEach(async (to, from, next) => {
    if (to.params.masterCategoryId) {
        const catalogStore = useCatalogStore();

        if (!catalogStore.categories || !catalogStore.categories.length) {
            try {
                await catalogStore.fetchCategories();
            } catch (error) {
                console.error('Error loading categories:', error);
            }
        }

        if (catalogStore.currentCategoryName) {
            document.title = `StyleShop - ${catalogStore.currentCategoryName}`;
        } else {
            document.title = 'StyleShop - Category';
        }
    } else {
        document.title = to.name === 'catalog' ? 'StyleShop - Catalog' : 'StyleShop';
    }

    next();
});

export default router
