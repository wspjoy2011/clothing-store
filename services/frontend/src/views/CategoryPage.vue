<template>
  <div class="category-page">
    <div class="container-custom mx-auto my-6">
      <!-- Breadcrumbs -->
      <v-breadcrumbs class="pa-0 mb-4">
        <v-breadcrumbs-item
            title="Home"
            prepend-icon="mdi-home"
            to="/"
        />
        <v-breadcrumbs-item
            title="Catalog"
            to="/catalog"
        />
        <template v-if="masterCategory">
          <v-breadcrumbs-item
              :title="masterCategory.name"
              :to="{ name: 'master-category', params: { masterCategory: masterCategorySlug } }"
              :disabled="route.name === 'master-category'"
          />
        </template>
        <template v-if="subCategory">
          <v-breadcrumbs-item
              :title="subCategory.name"
              :to="subCategorySlug ? { name: 'sub-category', params: { masterCategory: masterCategorySlug, subCategory: subCategorySlug } } : null"
              :disabled="route.name === 'sub-category' || !subCategorySlug"
          />
        </template>
        <template v-if="articleType">
          <v-breadcrumbs-item
              :title="articleType.name"
              :disabled="true"
          />
        </template>
      </v-breadcrumbs>

      <!-- Category Header -->
      <div class="category-header mb-6">
        <h1 class="text-h4 font-weight-bold mb-2">
          {{ currentCategoryTitle }}
        </h1>
        <p class="text-subtitle-1" v-if="currentCategoryDescription">
          {{ currentCategoryDescription }}
        </p>
      </div>

      <!-- Debug Info -->
      <v-card class="mb-6 pa-4">
        <h3 class="text-h6 mb-2">Category Information</h3>
        <v-list>
          <v-list-item v-if="masterCategory">
            <template v-slot:prepend>
              <v-icon icon="mdi-tag" color="primary"></v-icon>
            </template>
            <v-list-item-title>Master Category: {{ masterCategory.name }}</v-list-item-title>
            <v-list-item-subtitle>
              ID: {{ masterCategoryId }} | Slug: {{ masterCategorySlug }}
            </v-list-item-subtitle>
          </v-list-item>

          <v-list-item v-if="subCategory">
            <template v-slot:prepend>
              <v-icon icon="mdi-tag-outline" color="secondary"></v-icon>
            </template>
            <v-list-item-title>Sub Category: {{ subCategory.name }}</v-list-item-title>
            <v-list-item-subtitle>
              ID: {{ subCategoryId }} | Slug: {{ subCategorySlug }}
            </v-list-item-subtitle>
          </v-list-item>

          <v-list-item v-if="articleType">
            <template v-slot:prepend>
              <v-icon icon="mdi-tshirt-crew-outline" color="success"></v-icon>
            </template>
            <v-list-item-title>Article Type: {{ articleType.name }}</v-list-item-title>
            <v-list-item-subtitle>
              ID: {{ articleTypeId }} | Slug: {{ articleTypeSlug }}
            </v-list-item-subtitle>
          </v-list-item>

          <v-list-item v-if="categoryPath && categoryPath.length > 0">
            <template v-slot:prepend>
              <v-icon icon="mdi-map-marker-path" color="info"></v-icon>
            </template>
            <v-list-item-title>Category Path:</v-list-item-title>
            <v-list-item-subtitle>
              {{ formattedCategoryPath }}
            </v-list-item-subtitle>
          </v-list-item>

          <v-list-item>
            <template v-slot:prepend>
              <v-icon icon="mdi-link-variant" color="warning"></v-icon>
            </template>
            <v-list-item-title>Current URL:</v-list-item-title>
            <v-list-item-subtitle>{{ currentPath }}</v-list-item-subtitle>
          </v-list-item>
        </v-list>
      </v-card>

      <content-loader v-if="isLoading"/>

      <v-card class="pa-4" v-if="!isLoading">
        <h3 class="text-h6 mb-3">Products will be loaded here</h3>
        <p>This is a placeholder that will be replaced with actual category products</p>
        <div class="mt-4">
          <v-btn
              color="primary"
              @click="$router.push('/catalog')"
              prepend-icon="mdi-arrow-left">
            Back to Catalog
          </v-btn>
        </div>
      </v-card>
    </div>
  </div>
</template>

<script setup>
import {computed, onMounted, ref, watch} from 'vue';
import {useRoute, useRouter} from 'vue-router';
import {useCategoryStore} from '@/stores/categoryStore';
import ContentLoader from '@/components/ui/loaders/ContentLoader.vue';

const route = useRoute();
const router = useRouter();
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

const masterCategory = ref(null);
const subCategory = ref(null);
const articleType = ref(null);
const isLoading = ref(true);

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

const categoryPath = computed(() => {
  return categoryStore.getCategoryPath(
      masterCategoryId.value,
      subCategoryId.value,
      articleTypeId.value
  );
});

const formattedCategoryPath = computed(() => {
  if (!categoryPath.value || !categoryPath.value.length) return '';

  return categoryPath.value
      .map(item => `${item.name} (${item.slug})`)
      .join(' > ');
});

const currentPath = computed(() => {
  let path = '/category/' + masterCategorySlug.value;
  if (subCategorySlug.value) {
    path += '/' + subCategorySlug.value;
    if (articleTypeSlug.value) {
      path += '/' + articleTypeSlug.value;
    }
  }
  return path;
});

const loadCategoryData = async () => {
  isLoading.value = true;

  try {
    if (!categoryStore.hasCategories) {
      await categoryStore.fetchCategoryMenu();
    }

    if (masterCategoryId.value) {
      const data = await categoryStore.loadCategoryData(
          masterCategoryId.value,
          subCategoryId.value,
          articleTypeId.value
      );

      masterCategory.value = data.masterCategory;
      subCategory.value = data.subCategory;
      articleType.value = data.articleType;
    } else {
      console.error("Could not find master category with slug:", masterCategorySlug.value);
    }
  } catch (error) {
    console.error('Error loading category data:', error);
  } finally {
    isLoading.value = false;
  }
};

watch(
    () => route.params,
    () => {
      loadCategoryData();
    },
    {deep: true}
);

onMounted(loadCategoryData);
</script>

<style scoped>
.container-custom {
  width: 100%;
  max-width: 1280px;
  padding: 0 16px;
  box-sizing: border-box;
}

.category-header {
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  padding-bottom: 16px;
}

@media (min-width: 960px) {
  .container-custom {
    padding: 0 24px;
  }
}

@media (min-width: 1440px) {
  .container-custom {
    max-width: 1400px;
  }
}

@media (min-width: 1920px) {
  .container-custom {
    max-width: 1600px;
  }
}
</style>
