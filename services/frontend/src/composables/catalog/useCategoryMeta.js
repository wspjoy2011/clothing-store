import {computed} from 'vue';
import {useCategoryStore} from '@/stores/categoryStore';

export function useCategoryMeta(route) {
    const categoryStore = useCategoryStore();

    const masterCategorySlug = computed(() => route.params.masterCategory);
    const subCategorySlug = computed(() => route.params.subCategory);
    const articleTypeSlug = computed(() => route.params.articleType);

    const masterCategoryId = computed(() => {
        return masterCategorySlug.value ?
            categoryStore.getMasterCategoryIdBySlug(masterCategorySlug.value) : null;
    });

    const subCategoryId = computed(() => {
        if (!masterCategoryId.value || !subCategorySlug.value) return null;
        return categoryStore.getSubCategoryIdBySlug(masterCategoryId.value, subCategorySlug.value);
    });

    const articleTypeId = computed(() => {
        if (!masterCategoryId.value || !subCategoryId.value || !articleTypeSlug.value) return null;
        return categoryStore.getArticleTypeIdBySlug(masterCategoryId.value, subCategoryId.value, articleTypeSlug.value);
    });

    const masterCategory = computed(() => {
        return masterCategoryId.value ?
            categoryStore.getMasterCategory(masterCategoryId.value) : null;
    });

    const subCategory = computed(() => {
        if (!masterCategoryId.value || !subCategoryId.value) return null;
        return categoryStore.getSubCategory(masterCategoryId.value, subCategoryId.value);
    });

    const articleType = computed(() => {
        if (!masterCategoryId.value || !subCategoryId.value || !articleTypeId.value) return null;
        return categoryStore.getArticleType(masterCategoryId.value, subCategoryId.value, articleTypeId.value);
    });

    const currentCategoryTitle = computed(() => {
        return categoryStore.getCategoryName(
            masterCategoryId.value,
            subCategoryId.value,
            articleTypeId.value
        );
    });

    const currentCategoryDescription = computed(() => {
        return categoryStore.getCategoryDescription(
            masterCategoryId.value,
            subCategoryId.value,
            articleTypeId.value
        );
    });

    return {
        // Slugs
        masterCategorySlug,
        subCategorySlug,
        articleTypeSlug,

        // IDs
        masterCategoryId,
        subCategoryId,
        articleTypeId,

        // Objects
        masterCategory,
        subCategory,
        articleType,

        // Meta
        currentCategoryTitle,
        currentCategoryDescription
    };
}
