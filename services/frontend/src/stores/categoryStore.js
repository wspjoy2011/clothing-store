import {defineStore} from 'pinia';
import categoryService from "@/services/categoryService.js";
import router from '@/router';

const createSlug = (name) => {
    return name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
};

export const useCategoryStore = defineStore('category', {
    state: () => ({
        categories: [],
        loading: false,
        error: null,
        categoryMenuOpen: false,
        mobileDrawerOpen: false
    }),

    getters: {
        hasCategories: (state) => state.categories.length > 0,

        getMasterCategory: (state) => (id) => {
            if (!id) return null;
            return state.categories.find(cat => cat.id.toString() === id.toString());
        },

        getMasterCategorySlug: (state) => (id) => {
            const category = state.categories.find(cat => cat.id.toString() === id.toString());
            return category ? createSlug(category.name) : '';
        },

        getMasterCategoryIdBySlug: (state) => (slug) => {
            if (!slug) return null;
            const category = state.categories.find(cat => createSlug(cat.name) === slug);
            return category ? category.id : null;
        },

        getSubCategory: (state) => (masterId, subId) => {
            if (!masterId || !subId) return null;
            const master = state.categories.find(cat => cat.id.toString() === masterId.toString());
            if (!master || !master.sub_categories) return null;

            return master.sub_categories.find(sub => sub.id.toString() === subId.toString());
        },

        // Get slug for subcategory
        getSubCategorySlug: (state) => (masterId, subId) => {
            if (!masterId || !subId) return '';
            const master = state.categories.find(cat => cat.id.toString() === masterId.toString());
            if (!master || !master.sub_categories) return '';

            const sub = master.sub_categories.find(sub => sub.id.toString() === subId.toString());
            return sub ? createSlug(sub.name) : '';
        },

        getSubCategoryIdBySlug: (state) => (masterId, slug) => {
            if (!masterId || !slug) return null;
            const master = state.categories.find(cat => cat.id.toString() === masterId.toString());
            if (!master || !master.sub_categories) return null;

            const sub = master.sub_categories.find(sub => createSlug(sub.name) === slug);
            return sub ? sub.id : null;
        },

        getArticleType: (state) => (masterId, subId, articleId) => {
            if (!masterId || !subId || !articleId) return null;
            const master = state.categories.find(cat => cat.id.toString() === masterId.toString());
            if (!master || !master.sub_categories) return null;

            const sub = master.sub_categories.find(sub => sub.id.toString() === subId.toString());
            if (!sub || !sub.article_types) return null;

            return sub.article_types.find(art => art.id.toString() === articleId.toString());
        },

        getArticleTypeSlug: (state) => (masterId, subId, articleId) => {
            if (!masterId || !subId || !articleId) return '';
            const master = state.categories.find(cat => cat.id.toString() === masterId.toString());
            if (!master || !master.sub_categories) return '';

            const sub = master.sub_categories.find(sub => sub.id.toString() === subId.toString());
            if (!sub || !sub.article_types) return '';

            const article = sub.article_types.find(art => art.id.toString() === articleId.toString());
            return article ? createSlug(article.name) : '';
        },

        getArticleTypeIdBySlug: (state) => (masterId, subId, slug) => {
            if (!masterId || !subId || !slug) return null;
            const master = state.categories.find(cat => cat.id.toString() === masterId.toString());
            if (!master || !master.sub_categories) return null;

            const sub = master.sub_categories.find(sub => sub.id.toString() === subId.toString());
            if (!sub || !sub.article_types) return null;

            const article = sub.article_types.find(art => createSlug(art.name) === slug);
            return article ? article.id : null;
        },

        getCategoryName: (state) => (masterId, subId, articleId) => {
            if (!masterId) return 'Category';

            const master = state.categories.find(cat => cat.id.toString() === masterId.toString());
            if (!master) return 'Category';

            if (!subId) return master.name;

            const sub = master.sub_categories?.find(sub => sub.id.toString() === subId.toString());
            if (!sub) return master.name;

            if (!articleId) return sub.name;

            const article = sub.article_types?.find(art => art.id.toString() === articleId.toString());
            return article ? article.name : sub.name;
        },

        getCategoryDescription: (state) => (masterId, subId, articleId) => {
            if (!masterId) return '';

            const master = state.categories.find(cat => cat.id.toString() === masterId.toString());
            if (!master) return '';

            if (!subId) return master.description || '';

            const sub = master.sub_categories?.find(sub => sub.id.toString() === subId.toString());
            if (!sub) return master.description || '';

            if (!articleId) return sub.description || '';

            const article = sub.article_types?.find(art => art.id.toString() === articleId.toString());
            return article ? (article.description || '') : (sub.description || '');
        },

        getCategoryPath: (state) => (masterId, subId, articleId) => {
            const result = [];

            if (!masterId) return result;

            const master = state.categories.find(cat => cat.id.toString() === masterId.toString());
            if (!master) return result;

            result.push({
                id: master.id,
                name: master.name,
                type: 'master',
                slug: createSlug(master.name)
            });

            if (!subId) return result;

            const sub = master.sub_categories?.find(sub => sub.id.toString() === subId.toString());
            if (!sub) return result;

            result.push({
                id: sub.id,
                name: sub.name,
                type: 'sub',
                parentId: master.id,
                slug: createSlug(sub.name)
            });

            if (!articleId) return result;

            const article = sub.article_types?.find(art => art.id.toString() === articleId.toString());
            if (!article) return result;

            result.push({
                id: article.id,
                name: article.name,
                type: 'article',
                parentId: sub.id,
                grandParentId: master.id,
                slug: createSlug(article.name)
            });

            return result;
        }
    },

    actions: {
        async fetchCategoryMenu() {
            if (this.categories.length > 0 && !this.loading) {
                return;
            }

            this.loading = true;
            this.error = null;

            try {
                const response = await categoryService.getCategoryMenu();
                this.categories = response.categories || [];
            } catch (error) {
                this.error = error.message || 'Failed to load categories';
                console.error('Category menu fetch error:', error);
            } finally {
                this.loading = false;
            }
        },

        closeMenus() {
            this.categoryMenuOpen = false;
            this.mobileDrawerOpen = false;
        },

        navigateToCategory(categoryInfo) {
            console.log('Navigating to category via store:', categoryInfo);

            this.closeMenus();

            if (!categoryInfo || !categoryInfo.type || !categoryInfo.id) {
                console.error('Invalid category info:', categoryInfo);
                return;
            }

            const {type, id, name} = categoryInfo;
            const slug = createSlug(name);

            if (type === 'master') {
                router.push({
                    name: 'master-category',
                    params: {masterCategory: slug}
                });
            } else if (type === 'sub') {
                const parentId = categoryInfo.parentId;
                if (!parentId) {
                    console.error('Missing parentId for sub-category navigation');
                    return;
                }

                const masterCategory = this.getMasterCategory(parentId);
                if (!masterCategory) {
                    console.error('Master category not found for parentId:', parentId);
                    return;
                }

                router.push({
                    name: 'sub-category',
                    params: {
                        masterCategory: createSlug(masterCategory.name),
                        subCategory: slug
                    }
                });
            } else if (type === 'article') {
                const parentId = categoryInfo.parentId;
                const grandParentId = categoryInfo.grandParentId;

                if (!parentId || !grandParentId) {
                    console.error('Missing parentId or grandParentId for article-type navigation');
                    return;
                }

                const masterCategory = this.getMasterCategory(grandParentId);
                if (!masterCategory) {
                    console.error('Master category not found for grandParentId:', grandParentId);
                    return;
                }

                const subCategory = this.getSubCategory(grandParentId, parentId);
                if (!subCategory) {
                    console.error('Sub category not found for parentId:', parentId);
                    return;
                }

                router.push({
                    name: 'article-type',
                    params: {
                        masterCategory: createSlug(masterCategory.name),
                        subCategory: createSlug(subCategory.name),
                        articleType: slug
                    }
                });
            }
        },

        async loadCategoryData(masterId, subId = null, articleId = null) {
            if (!this.hasCategories && !this.loading) {
                await this.fetchCategoryMenu();
            }

            return {
                masterCategory: this.getMasterCategory(masterId),
                subCategory: subId ? this.getSubCategory(masterId, subId) : null,
                articleType: articleId ? this.getArticleType(masterId, subId, articleId) : null
            };
        },

        getAllMasterCategories() {
            return this.categories;
        },

        getSubCategoriesFor(masterId) {
            const master = this.getMasterCategory(masterId);
            return master?.sub_categories || [];
        },

        getArticleTypesFor(masterId, subId) {
            const sub = this.getSubCategory(masterId, subId);
            return sub?.article_types || [];
        }
    }
});
