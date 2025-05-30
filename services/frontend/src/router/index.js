import {createRouter, createWebHistory} from 'vue-router'
import { useUserPreferencesStore } from '@/stores/userPreferences'
import { useCatalogStore } from '@/stores/catalog'
import { useCategoryStore } from '@/stores/categoryStore'

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
    const categoryStore = useCategoryStore();

    const masterCategoryId = categoryStore.getMasterCategoryIdBySlug(route.params.masterCategory);
    const subCategoryId = route.params.subCategory ?
        categoryStore.getSubCategoryIdBySlug(masterCategoryId, route.params.subCategory) : null;
    const articleTypeId = route.params.articleType ?
        categoryStore.getArticleTypeIdBySlug(masterCategoryId, subCategoryId, route.params.articleType) : null;

    return {
        masterCategoryId,
        subCategoryId,
        articleTypeId,
        masterCategorySlug: route.params.masterCategory,
        subCategorySlug: route.params.subCategory,
        articleTypeSlug: route.params.articleType
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
        path: '/category/:masterCategory',
        name: 'master-category',
        component: CategoryPage,
        props: processCategoryRouteProps
    },
    {
        path: '/category/:masterCategory/:subCategory',
        name: 'sub-category',
        component: CategoryPage,
        props: processCategoryRouteProps
    },
    {
        path: '/category/:masterCategory/:subCategory/:articleType',
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
    const categoryStore = useCategoryStore();

    if (to.params.masterCategory) {
        if (!categoryStore.categories || !categoryStore.categories.length) {
            try {
                await categoryStore.fetchCategoryMenu();
            } catch (error) {
                console.error('Error loading categories:', error);
            }
        }

        const masterCategoryId = categoryStore.getMasterCategoryIdBySlug(to.params.masterCategory);
        const subCategoryId = to.params.subCategory ?
            categoryStore.getSubCategoryIdBySlug(masterCategoryId, to.params.subCategory) : null;
        const articleTypeId = to.params.articleType ?
            categoryStore.getArticleTypeIdBySlug(masterCategoryId, subCategoryId, to.params.articleType) : null;

        if (!masterCategoryId) {
            console.error('Category not found:', to.params.masterCategory);
            next({ name: 'home' });
            return;
        }

        if (articleTypeId) {
            const articleName = categoryStore.getCategoryName(masterCategoryId, subCategoryId, articleTypeId);
            document.title = `StyleShop - ${articleName}`;
        } else if (subCategoryId) {
            const subName = categoryStore.getCategoryName(masterCategoryId, subCategoryId);
            document.title = `StyleShop - ${subName}`;
        } else {
            const masterName = categoryStore.getCategoryName(masterCategoryId);
            document.title = `StyleShop - ${masterName}`;
        }
    } else {
        document.title = to.name === 'catalog' ? 'StyleShop - Catalog' : 'StyleShop';
    }

    next();
});

export default router
