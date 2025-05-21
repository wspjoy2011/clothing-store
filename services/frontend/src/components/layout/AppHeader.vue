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
                  <category-menu
                      @category-select="navigateToCategory"
                      :onCategoryClick="navigateToCategory"
                  />
                </div>
              </v-menu>
            </v-tab>
          </v-tabs>
        </div>

        <!-- Right Side Icons -->
        <div class="d-flex align-center">
          <!-- Theme Toggle -->
          <theme-toggle class="mr-2"/>

          <!-- Search Button and Input -->
          <search-bar class="mr-2"/>

          <!-- User Account -->
          <v-btn icon class="mr-2">
            <v-icon>mdi-account</v-icon>
          </v-btn>

          <!-- Shopping Cart with Badge -->
          <v-btn icon>
            <v-badge
                color="error"
                content="2"
                dot
            >
              <v-icon>mdi-cart</v-icon>
            </v-badge>
          </v-btn>

          <!-- Mobile Menu Button -->
          <v-btn
              icon
              class="ml-4 hidden-md-and-up"
              @click="drawer = !drawer"
          >
            <v-icon>mdi-menu</v-icon>
          </v-btn>
        </div>
      </div>
    </v-container>
  </v-app-bar>

  <!-- Mobile Navigation Drawer -->
  <v-navigation-drawer
      v-model="drawer"
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
          <category-menu
              @category-select="navigateToCategory"
              :onCategoryClick="navigateToCategory"
          />
        </div>
      </v-list-group>

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
import {ref, watch, onMounted} from 'vue';
import {useTheme} from 'vuetify';
import {useRouter, useRoute} from 'vue-router';
import {useCatalogStore} from '@/stores/catalog';
import {useCategoryStore} from '@/stores/categoryStore';
import ThemeToggle from '@/components/ui/theme/ThemeToggle.vue';
import SearchBar from '@/components/ui/search/SearchBar.vue';
import CategoryMenu from '@/components/catalog/CategoryMenu.vue';
import {useUserPreferencesStore} from '@/stores/userPreferences';

const activeTab = ref('home');
const drawer = ref(false);
const theme = useTheme();
const router = useRouter();
const route = useRoute();
const catalogStore = useCatalogStore();
const categoryStore = useCategoryStore();
const preferencesStore = useUserPreferencesStore();
const showMobileSearch = ref(false);
const mobileSearchQuery = ref('');
const isSearchLoading = ref(false);

onMounted(() => {
  activeTab.value = route.name || 'home';

  if (route.query.q) {
    mobileSearchQuery.value = route.query.q;
  }

  if (!categoryStore.hasCategories && !categoryStore.loading) {
    categoryStore.fetchCategoryMenu();
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
  }
});

function toggleTheme() {
  const newTheme = preferencesStore.theme === 'dark' ? 'light' : 'dark';
  preferencesStore.setTheme(newTheme);
  theme.global.name.value = newTheme;
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

      router.push({
        name: 'catalog',
        query
      });
    }
  }
}

function handleMobileSearch() {
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

  router.push({
    name: 'catalog',
    query
  }).then(() => {
    showMobileSearch.value = false;
    isSearchLoading.value = false;

    if (route.name === 'catalog') {
      catalogStore.fetchProducts(1);
    }
  }).catch(() => {
    isSearchLoading.value = false;
  });
}

function navigateToCategory(categoryInfo) {
  console.log('Navigating to category:', categoryInfo);

  drawer.value = false;

  router.push({
    name: 'catalog',
    query: {
      [`${categoryInfo.type}_category_id`]: categoryInfo.id,
      page: 1
    }
  });
}
</script>

<style scoped>
.header {
  background: linear-gradient(145deg, #fdfbfb 0%, #ebedee 100%);
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
}

:deep(.v-theme--dark) .category-dropdown {
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3);
}
</style>
