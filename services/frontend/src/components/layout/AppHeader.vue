<template>
  <v-app-bar
      app
      elevation="2"
      class="header"
  >
    <v-container>
      <div class="d-flex align-center justify-space-between">
        <!-- Logo and Brand Name -->
        <app-header-brand
            :show-category-path="showCategoryPath"
            :category-path-visible="categoryPathVisible"
            :short-category-path-text="shortCategoryPathText"
            @go-to-home="goToHome"
            @toggle-category-path="toggleCategoryPathVisible"
        />

        <!-- Navigation Menu -->
        <app-header-navigation
            v-model:active-tab="activeTab"
            v-model:category-menu-open="categoryStore.categoryMenuOpen"
        />

        <!-- Right Side Icons -->
        <app-header-actions
            :show-category-path="showCategoryPath"
            @go-to-cart="goToCart"
            @toggle-category-path="toggleCategoryPathVisible"
            @toggle-mobile-drawer="toggleMobileDrawer"
        >
          <template #user-menu>
            <app-header-user-menu
                :is-authenticated="isAuthenticated"
                :current-user="currentUser"
                :user-display-name="userDisplayName"
                :user-email="userEmail"
                @go-to-login="goToLogin"
                @go-to-account-settings="goToAccountSettings"
                @go-to-profile="goToProfile"
                @go-to-change-password="goToChangePassword"
                @go-to-wishlist="goToWishlist"
                @go-to-order-history="goToOrderHistory"
                @handle-logout="handleLogout"
            />
          </template>
        </app-header-actions>
      </div>
    </v-container>
  </v-app-bar>

  <!-- Category Path Dropdown -->
  <app-header-category-path
      :show-category-path="showCategoryPath"
      :category-path-visible="categoryPathVisible"
      :is-dark-theme="isDarkTheme"
      :current-category-path="currentCategoryPath"
      @navigate-to-category="navigateToPathCategory"
      @close-category-path="categoryPathVisible = false"
  />

  <!-- Mobile Navigation Drawer -->
  <app-header-mobile-drawer
      v-model:mobile-drawer-open="categoryStore.mobileDrawerOpen"
      :show-category-path="showCategoryPath"
      :current-category-path="currentCategoryPath"
      :is-authenticated="isAuthenticated"
      :current-user="currentUser"
      :user-display-name="userDisplayName"
      @navigate-to-category="navigateToPathCategory"
      @go-to-account-settings="goToAccountSettings"
      @go-to-profile="goToProfile"
      @go-to-change-password="goToChangePassword"
      @go-to-wishlist="goToWishlist"
      @go-to-order-history="goToOrderHistory"
      @handle-logout="handleLogout"
      @go-to-login="goToLogin"
      @show-mobile-search="showMobileSearch = true"
      @go-to-cart="goToCart"
      @toggle-theme="toggleTheme"
  />

  <!-- Mobile Search Dialog -->
  <app-header-mobile-search
      v-model:show-mobile-search="showMobileSearch"
      v-model:mobile-search-query="mobileSearchQuery"
      :is-search-loading="isSearchLoading"
      @close-mobile-search="closeMobileSearch"
      @handle-mobile-search="handleMobileSearch"
      @clear-mobile-search="clearMobileSearch"
  />
</template>

<script setup>
import {useAppHeader} from '@/composables/layout/useAppHeader'
import AppHeaderBrand from '@/components/layout/header/AppHeaderBrand.vue'
import AppHeaderNavigation from '@/components/layout/header/AppHeaderNavigation.vue'
import AppHeaderUserMenu from '@/components/layout/header/AppHeaderUserMenu.vue'
import AppHeaderActions from '@/components/layout/header/AppHeaderActions.vue'
import AppHeaderCategoryPath from '@/components/layout/header/AppHeaderCategoryPath.vue'
import AppHeaderMobileDrawer from '@/components/layout/header/AppHeaderMobileDrawer.vue'
import AppHeaderMobileSearch from '@/components/layout/header/AppHeaderMobileSearch.vue'

const {
  // State
  activeTab,
  showMobileSearch,
  mobileSearchQuery,
  isSearchLoading,
  categoryPathVisible,

  // Computed
  isAuthenticated,
  currentUser,
  userEmail,
  userDisplayName,
  isDarkTheme,
  currentCategoryPath,
  showCategoryPath,
  shortCategoryPathText,

  // Store state
  categoryStore,

  // Methods
  toggleCategoryPathVisible,
  toggleTheme,
  toggleMobileDrawer,
  clearMobileSearch,
  closeMobileSearch,
  handleMobileSearch,
  navigateToPathCategory,

  // Navigation methods
  goToLogin,
  goToAccountSettings,
  goToWishlist,
  goToProfile,
  goToOrderHistory,
  goToCart,
  goToHome,
  goToChangePassword,
  handleLogout
} = useAppHeader()
</script>

<style scoped>
.header {
  background: linear-gradient(145deg, #fdfbfb 0%, #ebedee 100%);
  z-index: 100;
}

:deep(.v-app-bar.v-theme--dark) {
  background: linear-gradient(145deg, #1a1a1a 0%, #2c2c2c 100%);
}
</style>
