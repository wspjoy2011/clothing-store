import {createRouter, createWebHistory} from 'vue-router'
import {useUserPreferencesStore} from '@/stores/userPreferences'
import {useCatalogStore} from '@/stores/catalog'
import {useCategoryStore} from '@/stores/categoryStore'
import {useAccountStore} from '@/stores/accounts'

import HomePage from '@/views/HomePage.vue'
import CatalogPage from '@/views/CatalogPage.vue'
import CategoryPage from '@/views/CategoryPage.vue'
import ProductDetailPage from '@/views/ProductDetailPage.vue'
import RegisterPage from '@/views/RegisterPage.vue'
import LoginPage from '@/views/LoginPage.vue'
import ActivatePage from '@/views/ActivatePage.vue'
import ResendActivationPage from '@/views/ResendActivationPage.vue'
import LogoutPage from '@/views/LogoutPage.vue'

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

const processProductRouteProps = (route) => {
    const catalogStore = useCatalogStore();

    const productId = catalogStore.getProductIdBySlug(route.params.productSlug);

    return {
        productSlug: route.params.productSlug,
        productId: productId
    }
};

const processActivationRouteProps = (route) => {
    return {
        email: route.query.email || '',
        token: route.query.token || ''
    }
};

const processResendActivationRouteProps = (route) => {
    return {
        email: route.query.email || ''
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
        path: '/product/:productSlug',
        name: 'product-detail',
        component: ProductDetailPage,
        props: processProductRouteProps
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
    },
    {
        path: '/accounts/register',
        name: 'register',
        component: RegisterPage,
        meta: {
            title: 'Register - StyleShop',
            requiresGuest: true
        }
    },
    {
        path: '/accounts/login',
        name: 'login',
        component: LoginPage,
        meta: {
            title: 'Login - StyleShop',
            requiresGuest: true
        }
    },
    {
        path: '/accounts/logout',
        name: 'logout',
        component: LogoutPage,
        meta: {
            title: 'Logout - StyleShop',
            requiresAuth: true
        }
    },
    {
        path: '/accounts/activate',
        name: 'activate',
        component: ActivatePage,
        props: processActivationRouteProps,
        meta: {
            title: 'Activate Account - StyleShop',
            requiresGuest: true
        }
    },
    {
        path: '/accounts/resend-activation',
        name: 'resend-activation',
        component: ResendActivationPage,
        props: processResendActivationRouteProps,
        meta: {
            title: 'Resend Activation - StyleShop',
            requiresGuest: true
        }
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
    const accountStore = useAccountStore();

    if (!accountStore.isInitialized) {
        await accountStore.initializeAuth();
    }

    if (to.meta.requiresAuth && !accountStore.isAuthenticated) {
        console.log('Access denied: authentication required');
        next({
            name: 'login',
            query: { redirect: to.fullPath }
        });
        return;
    }

    if (to.meta.requiresGuest && accountStore.isAuthenticated) {
        console.log('Access denied: already authenticated');
        next({ name: 'home' });
        return;
    }

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
            next({name: 'home'});
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
        if (to.name === 'product-detail') {
            document.title = 'StyleShop - Product Details';
        } else if (to.name === 'register') {
            document.title = 'StyleShop - Register';
        } else if (to.name === 'login') {
            document.title = 'StyleShop - Login';
        } else if (to.name === 'logout') {
            document.title = 'StyleShop - Logout';
        } else if (to.name === 'activate') {
            document.title = 'StyleShop - Activate Account';
        } else if (to.name === 'resend-activation') {
            document.title = 'StyleShop - Resend Activation';
        } else {
            document.title = to.name === 'catalog' ? 'StyleShop - Catalog' : 'StyleShop';
        }
    }

    next();
});

export default router
