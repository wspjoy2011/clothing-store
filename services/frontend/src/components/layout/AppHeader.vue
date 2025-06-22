<template>
  <v-app-bar
      app
      elevation="2"
      class="header"
  >
    <v-container>
      <div class="d-flex align-center justify-space-between">
        <!-- Logo and Brand Name -->
        <div class="d-flex align-center">
          <v-icon icon="mdi-store" size="large" class="mr-2"></v-icon>
          <span class="text-h5 font-weight-bold">StyleShop</span>

          <!-- Category Path Indicator -->
          <v-btn
              v-if="showCategoryPath"
              variant="text"
              class="ml-3 category-path-indicator hidden-md-and-down"
              @click="toggleCategoryPathVisible"
          >
            <v-icon icon="mdi-tag-multiple" class="mr-1" size="small"></v-icon>
            <span class="text-subtitle-2">{{ shortCategoryPathText }}</span>
            <v-icon :icon="categoryPathVisible ? 'mdi-chevron-up' : 'mdi-chevron-down'" class="ml-1"
                    size="small"></v-icon>
          </v-btn>
        </div>

        <!-- Navigation Menu -->
        <div class="hidden-sm-and-down nav-center">
          <v-tabs
              v-model="activeTab"
              centered
          >
            <v-tab :to="{ name: 'home' }" value="home">Home</v-tab>
            <v-tab :to="{ name: 'catalog' }" value="catalog">Catalog</v-tab>

            <v-tab value="categories">
              Categories
              <v-menu
                  v-model="categoryStore.categoryMenuOpen"
                  location="bottom"
                  :close-on-content-click="false"
                  transition="slide-y-transition"
              >
                <template v-slot:activator="{ props }">
                  <v-btn
                      icon
                      variant="text"
                      v-bind="props"
                      class="ml-1"
                  >
                    <v-icon>mdi-chevron-down</v-icon>
                  </v-btn>
                </template>

                <div class="category-dropdown">
                  <category-menu/>
                </div>
              </v-menu>
            </v-tab>
          </v-tabs>
        </div>

        <!-- Right Side Icons -->
        <div class="d-flex align-center">
          <theme-toggle class="mr-2"/>

          <search-bar class="mr-2"/>

          <!-- Account Menu -->
          <v-menu location="bottom end" transition="slide-y-transition">
            <template v-slot:activator="{ props }">
              <v-btn icon class="mr-2" v-bind="props">
                <v-icon>mdi-account</v-icon>
              </v-btn>
            </template>

            <v-card min-width="200">
              <v-list>
                <v-list-item
                    :to="{ name: 'register' }"
                    prepend-icon="mdi-account-plus"
                    title="Register"
                    subtitle="Create new account"
                ></v-list-item>

                <v-list-item
                    prepend-icon="mdi-login"
                    title="Sign In"
                    subtitle="Access your account"
                    @click="goToLogin"
                ></v-list-item>

                <v-divider></v-divider>

                <v-list-item
                    prepend-icon="mdi-account-cog"
                    title="Account Settings"
                    @click="goToSettings"
                ></v-list-item>

                <v-list-item
                    prepend-icon="mdi-heart"
                    title="Wishlist"
                    @click="goToWishlist"
                ></v-list-item>
              </v-list>
            </v-card>
          </v-menu>

          <v-btn icon>
            <v-badge
                color="error"
                content="2"
                dot
            >
              <v-icon>mdi-cart</v-icon>
            </v-badge>
          </v-btn>

          <!-- Category Path Indicator for Mobile -->
          <v-btn
              v-if="showCategoryPath"
              icon
              class="ml-2 hidden-lg-and-up"
              @click="toggleCategoryPathVisible"
          >
            <v-badge
                color="primary"
                dot
            >
              <v-icon>mdi-tag-multiple</v-icon>
            </v-badge>
          </v-btn>

          <!-- Mobile Menu Button -->
          <v-btn
              icon
              class="ml-2 hidden-md-and-up"
              @click="toggleMobileDrawer"
          >
            <v-icon>mdi-menu</v-icon>
          </v-btn>
        </div>
      </div>
    </v-container>
  </v-app-bar>

  <div
      v-if="showCategoryPath && categoryPathVisible"
      class="category-path-dropdown"
      :class="{ 'theme-dark': isDarkTheme }"
  >
    <v-container>
      <div class="d-flex align-center justify-space-between">
        <div class="category-breadcrumbs">
          <v-chip-group>
            <v-chip
                v-for="(category, index) in currentCategoryPath"
                :key="index"
                :color="getCategoryChipColor(category.type)"
                variant="elevated"
                size="small"
                :class="['mr-1', `text-${getCategoryChipColor(category.type)}`]"
                @click="navigateToPathCategory(category, index)"
            >
              <v-icon
                  start
                  :icon="getCategoryIcon(category.type)"
                  size="small"
              ></v-icon>
              {{ category.name }}
            </v-chip>
          </v-chip-group>
        </div>
        <v-btn
            icon
            variant="text"
            @click="categoryPathVisible = false"
            size="small"
        >
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </div>
    </v-container>
  </div>

  <!-- Mobile Navigation Drawer -->
  <v-navigation-drawer
      v-model="categoryStore.mobileDrawerOpen"
      temporary
      location="right"
  >
    <v-list>
      <v-list-item
          title="Home"
          value="home"
          prepend-icon="mdi-home"
          :to="{ name: 'home' }"
      ></v-list-item>

      <v-list-item
          title="Catalog"
          value="catalog"
          prepend-icon="mdi-view-grid"
          :to="{ name: 'catalog' }"
      ></v-list-item>

      <v-list-group
          value="categories"
          title="Categories"
          prepend-icon="mdi-shape"
      >
        <template v-slot:activator="{ props }">
          <v-list-item v-bind="props"></v-list-item>
        </template>

        <div class="pa-2">
          <category-menu/>
        </div>
      </v-list-group>

      <!-- Current Category Path -->
      <template v-if="showCategoryPath">
        <v-divider class="my-2"></v-divider>
        <v-list-subheader>Current Category</v-list-subheader>

        <v-list-item
            v-for="(category, index) in currentCategoryPath"
            :key="`mobile-path-${index}`"
            :title="category.name"
            :prepend-icon="getCategoryIcon(category.type)"
            :value="category.id"
            @click="navigateToPathCategory(category, index)"
        >
        </v-list-item>
      </template>

      <v-divider></v-divider>

      <!-- Account Section -->
      <v-list-subheader>Account</v-list-subheader>

      <v-list-item
          title="Register"
          :to="{ name: 'register' }"
          prepend-icon="mdi-account-plus"
      ></v-list-item>

      <v-list-item
          title="Sign In"
          prepend-icon="mdi-login"
          @click="goToLogin"
      ></v-list-item>

      <v-divider></v-divider>

      <v-list-item
          title="New Arrivals"
          value="new"
          prepend-icon="mdi-star"
      ></v-list-item>

      <v-list-item
          title="Sale"
          value="sale"
          prepend-icon="mdi-tag"
      ></v-list-item>

      <v-divider></v-divider>

      <v-list-item
          title="Search"
          @click="showMobileSearch = true"
          prepend-icon="mdi-magnify"
      ></v-list-item>

      <v-list-item
          title="My Account"
          value="account"
          prepend-icon="mdi-account"
          @click="goToSettings"
      ></v-list-item>

      <v-list-item
          title="Shopping Cart"
          value="cart"
          prepend-icon="mdi-cart"
      ></v-list-item>

      <v-list-item
          title="Toggle Theme"
          @click="toggleTheme"
          prepend-icon="mdi-theme-light-dark"
      ></v-list-item>
    </v-list>
  </v-navigation-drawer>

  <!-- Mobile Search Dialog -->
  <v-dialog v-model="showMobileSearch" fullscreen transition="dialog-bottom-transition">
    <v-card>
      <v-toolbar density="compact" color="primary">
        <v-btn icon @click="closeMobileSearch">
          <v-icon>mdi-close</v-icon>
        </v-btn>
        <v-toolbar-title>Search</v-toolbar-title>
      </v-toolbar>
      <v-card-text class="pt-4">
        <v-text-field
            v-model="mobileSearchQuery"
            placeholder="Search products..."
            variant="outlined"
            prepend-inner-icon="mdi-magnify"
            clearable
            autofocus
            @keyup.enter="handleMobileSearch"
        >
          <template v-slot:append>
            <v-progress-circular
                v-if="isSearchLoading"
                indeterminate
                size="20"
                width="2"
                color="primary"
                class="mr-2"
            ></v-progress-circular>
            <v-btn
                v-else-if="mobileSearchQuery"
                icon="mdi-close"
                size="small"
                variant="text"
                @click="clearMobileSearch"
            ></v-btn>
          </template>
        </v-text-field>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script setup>
import {ref, watch, onMounted, computed, nextTick} from 'vue';
import {useTheme} from 'vuetify';
import {useRouter, useRoute} from 'vue-router';
import {useCatalogStore} from '@/stores/catalog';
import {useCategoryStore} from '@/stores/categoryStore';
import {useNavigation} from '@/composables/accounts/useNavigation';
import ThemeToggle from '@/components/ui/theme/ThemeToggle.vue';
import SearchBar from '@/components/ui/search/SearchBar.vue';
import CategoryMenu from '@/components/catalog/CategoryMenu.vue';
import {useUserPreferencesStore} from '@/stores/userPreferences';

const activeTab = ref('home');
const theme = useTheme();
const router = useRouter();
const route = useRoute();
const catalogStore = useCatalogStore();
const categoryStore = useCategoryStore();
const preferencesStore = useUserPreferencesStore();
const showMobileSearch = ref(false);
const mobileSearchQuery = ref('');
const isSearchLoading = ref(false);
const categoryPathVisible = ref(false);

const { goToLogin } = useNavigation();

const isDarkTheme = computed(() => {
  return theme.global.current.value.dark;
});

const isCategoryRoute = computed(() => {
  return route.name === 'master-category' ||
      route.name === 'sub-category' ||
      route.name === 'article-type';
});

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

const currentCategoryPath = computed(() => {
  if (!isCategoryRoute.value) return [];

  return categoryStore.getCategoryPath(
      masterCategoryId.value,
      subCategoryId.value,
      articleTypeId.value
  );
});

const showCategoryPath = computed(() => {
  return isCategoryRoute.value && currentCategoryPath.value.length > 0;
});

const shortCategoryPathText = computed(() => {
  if (!currentCategoryPath.value.length) return '';

  if (currentCategoryPath.value.length === 1) {
    return currentCategoryPath.value[0].name;
  }

  const lastCategory = currentCategoryPath.value[currentCategoryPath.value.length - 1];
  return `${lastCategory.name} (${currentCategoryPath.value.length} levels)`;
});

function toggleCategoryPathVisible() {
  categoryPathVisible.value = !categoryPathVisible.value;
}

function getCategoryChipColor(type) {
  switch (type) {
    case 'master':
      return 'primary';
    case 'sub':
      return 'secondary';
    case 'article':
      return 'success';
    default:
      return 'grey';
  }
}

function getCategoryIcon(type) {
  switch (type) {
    case 'master':
      return 'mdi-tag';
    case 'sub':
      return 'mdi-tag-outline';
    case 'article':
      return 'mdi-tshirt-crew-outline';
    default:
      return 'mdi-shape-outline';
  }
}

async function navigateToPathCategory(category, index) {
  if (!category || !category.type) return;

  categoryPathVisible.value = false;
  await nextTick();

  let routeName;
  const params = {};

  if (category.type === 'master') {
    routeName = 'master-category';
    params.masterCategory = category.slug;
  } else if (category.type === 'sub') {
    routeName = 'sub-category';
    const masterCategory = currentCategoryPath.value.find(c => c.type === 'master');
    if (!masterCategory) return;

    params.masterCategory = masterCategory.slug;
    params.subCategory = category.slug;
  } else if (category.type === 'article') {
    routeName = 'article-type';
    const masterCategory = currentCategoryPath.value.find(c => c.type === 'master');
    const subCategory = currentCategoryPath.value.find(c => c.type === 'sub');
    if (!masterCategory || !subCategory) return;

    params.masterCategory = masterCategory.slug;
    params.subCategory = subCategory.slug;
    params.articleType = category.slug;
  } else {
    return;
  }

  setTimeout(() => {
    router.push({
      name: routeName,
      params
    });
  }, 50);
}

function goToSettings() {
  // TODO: Navigate to account settings
  console.log('Navigate to account settings');
}

function goToWishlist() {
  // TODO: Navigate to wishlist
  console.log('Navigate to wishlist');
}

onMounted(async () => {
  activeTab.value = route.name || 'home';

  if (route.query.q) {
    mobileSearchQuery.value = route.query.q;
  }

  if (!categoryStore.hasCategories && !categoryStore.loading) {
    await categoryStore.fetchCategoryMenu();
  }

  if (isCategoryRoute.value) {
    activeTab.value = 'categories';
    categoryPathVisible.value = false;
  }
});

watch(() => catalogStore.searchQuery, (newValue) => {
  if (newValue !== mobileSearchQuery.value) {
    mobileSearchQuery.value = newValue;
  }
});

watch(() => route.name, (newName) => {
  if (newName) {
    activeTab.value = newName;

    if (newName === 'master-category' || newName === 'sub-category' || newName === 'article-type') {
      activeTab.value = 'categories';
      categoryPathVisible.value = false;
    } else {
      categoryPathVisible.value = false;
    }
  }
});

watch(() => route.params, () => {
  if (isCategoryRoute.value) {
    categoryPathVisible.value = false;
  }
}, {deep: true});

function toggleTheme() {
  const newTheme = preferencesStore.theme === 'dark' ? 'light' : 'dark';
  preferencesStore.setTheme(newTheme);
  theme.global.name.value = newTheme;
}

function toggleMobileDrawer() {
  categoryStore.mobileDrawerOpen = !categoryStore.mobileDrawerOpen;
}

function clearMobileSearch() {
  mobileSearchQuery.value = '';
}

function closeMobileSearch() {
  showMobileSearch.value = false;

  if (!mobileSearchQuery.value.trim() && catalogStore.searchQuery) {
    catalogStore.setSearchQuery('');
    if (route.name === 'catalog') {
      const query = {...route.query};
      delete query.q;
      delete query.page;

      setTimeout(() => {
        router.push({
          name: 'catalog',
          query
        });
      }, 50);
    }
  }
}

async function handleMobileSearch() {
  if (!mobileSearchQuery.value.trim() && !catalogStore.searchQuery) {
    closeMobileSearch();
    return;
  }

  isSearchLoading.value = true;
  const trimmedQuery = mobileSearchQuery.value.trim();

  catalogStore.setSearchQuery(trimmedQuery);

  const query = {...route.query};

  if (trimmedQuery) {
    query.q = trimmedQuery;
    delete query.page;
  } else {
    delete query.q;
  }

  showMobileSearch.value = false;
  await nextTick();

  setTimeout(() => {
    router.push({
      name: 'catalog',
      query
    }).then(() => {
      isSearchLoading.value = false;

      if (route.name === 'catalog') {
        catalogStore.fetchProducts(1);
      }
    }).catch((error) => {
      console.error('Navigation error:', error);
      isSearchLoading.value = false;
    });
  }, 50);
}
</script>

<style scoped>
.header {
  background: linear-gradient(145deg, #fdfbfb 0%, #ebedee 100%);
  z-index: 100;
}

:deep(.v-app-bar.v-theme--dark) {
  background: linear-gradient(145deg, #1a1a1a 0%, #2c2c2c 100%);
}

.nav-center {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
}

.category-dropdown {
  min-width: 320px;
  max-width: 85vw;
  padding: 0;
  max-height: 75vh;
  overflow-y: auto;
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
  background-color: #f5f5f5;
}

.category-path-indicator {
  display: flex;
  align-items: center;
  border-radius: 20px;
  padding: 0 12px;
  height: 32px;
  background-color: rgba(0, 0, 0, 0.05);
  transition: background-color 0.2s ease;
}

.category-path-indicator:hover {
  background-color: rgba(0, 0, 0, 0.1);
}

.category-path-dropdown {
  position: fixed;
  top: 64px;
  left: 0;
  right: 0;
  z-index: 99;
  background-color: #f5f5f5;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  padding: 16px 0;
  border-bottom-left-radius: 12px;
  border-bottom-right-radius: 12px;
  animation: slideDown 0.3s ease-out;
  font-size: 1.05rem;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.category-path-dropdown.theme-dark {
  background-color: #1E1E1E;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

:deep(.v-theme--dark) .category-path-indicator {
  background-color: rgba(255, 255, 255, 0.1);
}

:deep(.v-theme--dark) .category-path-indicator:hover {
  background-color: rgba(255, 255, 255, 0.15);
}

:deep(.v-theme--dark .category-dropdown) {
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3);
  background-color: #1E1E1E;
}

:deep(.v-theme--dark .category-menu) {
  background-color: #1E1E1E;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

:deep(.v-theme--dark .category-menu-container) {
  background-color: #1E1E1E;
}

:deep(.v-theme--dark .category-submenu-card) {
  background-color: #1E1E1E;
}

:deep(.v-theme--dark .nested-item-title:hover) {
  background-color: rgba(80, 80, 80, 0.3);
}

:deep(.v-theme--dark .category-btn) {
  background-color: #2A2A2A;
  color: rgba(255, 255, 255, 0.87);
}

.v-chip {
  background-color: #e0e0e0;
  color: rgba(0, 0, 0, 0.87);
  font-size: 0.95rem;
  font-weight: 500;
}

.v-chip.v-chip--elevated {
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.08);
}

.theme-dark .v-chip {
  background-color: #2A2A2A;
  color: rgba(255, 255, 255, 0.87);
}

.theme-dark .v-chip.v-chip--elevated {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.5);
}

.theme-dark .v-chip.text-primary {
  background-color: rgba(144, 202, 249, 0.15);
  color: #90CAF9;
}

.theme-dark .v-chip.text-secondary {
  background-color: rgba(97, 97, 97, 0.15);
  color: #616161;
}

.theme-dark .v-chip.text-success {
  background-color: rgba(129, 199, 132, 0.15);
  color: #81C784;
}

:deep(.v-theme--dark .v-list) {
  background-color: #1E1E1E;
  color: rgba(255, 255, 255, 0.87);
}

:deep(.v-theme--dark .v-list-item) {
  color: rgba(255, 255, 255, 0.87);
}

:deep(.v-theme--dark .v-list-subheader) {
  color: #90CAF9;
}

:deep(.v-theme--dark .v-divider) {
  border-color: rgba(255, 255, 255, 0.1);
}

:deep(.v-theme--dark .v-card) {
  background-color: #1E1E1E;
  color: rgba(255, 255, 255, 0.87);
}

:deep(.v-theme--dark .category-submenu)::-webkit-scrollbar {
  width: 8px;
}

:deep(.v-theme--dark .category-submenu)::-webkit-scrollbar-track {
  background: #1E1E1E;
}

:deep(.v-theme--dark .category-submenu)::-webkit-scrollbar-thumb {
  background: #424242;
  border-radius: 4px;
}

:deep(.v-theme--dark .category-submenu)::-webkit-scrollbar-thumb:hover {
  background: #555555;
}

.category-breadcrumbs {
  overflow-x: auto;
  white-space: nowrap;
  -ms-overflow-style: none;
  scrollbar-width: none;
}

.category-breadcrumbs::-webkit-scrollbar {
  display: none;
}

@media (max-width: 960px) {
  .category-path-dropdown {
    top: 56px;
  }
}
</style>
