<template>
  <v-navigation-drawer
      :model-value="mobileDrawerOpen"
      @update:model-value="$emit('update:mobile-drawer-open', $event)"
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
            @click="$emit('navigate-to-category', category, index)"
        >
        </v-list-item>
      </template>

      <v-divider></v-divider>

      <!-- Account Section -->
      <v-list-subheader>Account</v-list-subheader>

      <template v-if="isAuthenticated">
        <!-- Authenticated User Mobile Menu -->
        <v-list-item
            v-if="currentUser"
            class="mobile-user-info"
        >
          <template v-slot:prepend>
            <v-avatar size="24" color="primary">
              <v-icon icon="mdi-account" size="14"></v-icon>
            </v-avatar>
          </template>
          <v-list-item-title class="text-subtitle-2">
            {{ userDisplayName }}
          </v-list-item-title>
        </v-list-item>

        <v-list-item
            title="Account Settings"
            prepend-icon="mdi-account-cog"
            @click="$emit('go-to-account-settings')"
        ></v-list-item>

        <v-list-item
            title="Profile"
            prepend-icon="mdi-account"
            @click="$emit('go-to-profile')"
        ></v-list-item>

        <v-list-item
            title="Change Password"
            prepend-icon="mdi-lock-reset"
            @click="$emit('go-to-change-password')"
        ></v-list-item>

        <v-list-item
            title="Wishlist"
            prepend-icon="mdi-heart"
            @click="$emit('go-to-wishlist')"
        ></v-list-item>

        <v-list-item
            title="Order History"
            prepend-icon="mdi-history"
            @click="$emit('go-to-order-history')"
        ></v-list-item>

        <v-list-item
            title="Sign Out"
            prepend-icon="mdi-logout"
            @click="$emit('handle-logout')"
        ></v-list-item>
      </template>

      <template v-else>
        <!-- Guest User Mobile Menu -->
        <v-list-item
            title="Register"
            :to="{ name: 'register' }"
            prepend-icon="mdi-account-plus"
        ></v-list-item>

        <v-list-item
            title="Sign In"
            prepend-icon="mdi-login"
            @click="$emit('go-to-login')"
        ></v-list-item>
      </template>

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
          @click="$emit('show-mobile-search')"
          prepend-icon="mdi-magnify"
      ></v-list-item>

      <!-- Shopping Cart with dynamic info -->
      <v-list-item
          :title="cartTitle"
          :subtitle="cartSubtitle"
          value="cart"
          @click="$emit('go-to-cart')"
      >
        <template v-slot:prepend>
          <v-badge
              v-if="hasItems"
              color="error"
              dot
              offset-x="8"
              offset-y="8"
          >
            <v-icon>mdi-cart</v-icon>
          </v-badge>
          <v-icon v-else>mdi-cart</v-icon>
        </template>

        <template v-if="hasItems" v-slot:append>
          <v-chip
              size="x-small"
              color="error"
              variant="elevated"
              class="cart-chip"
          >
            {{ itemsCount }}
          </v-chip>
        </template>
      </v-list-item>

      <v-list-item
          title="Toggle Theme"
          @click="$emit('toggle-theme')"
          prepend-icon="mdi-theme-light-dark"
      ></v-list-item>
    </v-list>
  </v-navigation-drawer>
</template>

<script setup>
import { onMounted } from 'vue'
import CategoryMenu from '@/components/catalog/CategoryMenu.vue'
import { useCart } from '@/composables/cart/useCart.js'
import { useCartUI } from '@/composables/cart/useCartUI.js'

defineProps({
  mobileDrawerOpen: {
    type: Boolean,
    default: false
  },
  showCategoryPath: {
    type: Boolean,
    default: false
  },
  currentCategoryPath: {
    type: Array,
    default: () => []
  },
  isAuthenticated: {
    type: Boolean,
    default: false
  },
  currentUser: {
    type: Object,
    default: null
  },
  userDisplayName: {
    type: String,
    default: ''
  }
})

defineEmits([
  'update:mobile-drawer-open',
  'navigate-to-category',
  'go-to-account-settings',
  'go-to-profile',
  'go-to-change-password',
  'go-to-wishlist',
  'go-to-order-history',
  'handle-logout',
  'go-to-login',
  'show-mobile-search',
  'go-to-cart',
  'toggle-theme'
])

const cartData = useCart({ showNotifications: false })
const { hasItems, itemsCount, reloadCart } = cartData
const { cartTitle, cartSubtitle } = useCartUI(cartData)

onMounted(() => {
  reloadCart()
})

function getCategoryIcon(type) {
  switch (type) {
    case 'master':
      return 'mdi-tag'
    case 'sub':
      return 'mdi-tag-outline'
    case 'article':
      return 'mdi-tshirt-crew-outline'
    default:
      return 'mdi-shape-outline'
  }
}
</script>

<style scoped>
.mobile-user-info {
  background-color: rgb(from rgb(25, 118, 210) r g b / 0.1);
  margin-bottom: 8px;
}

.cart-chip {
  font-size: 10px;
  min-width: 20px;
  height: 20px;
}

:deep(.v-theme--dark) .mobile-user-info {
  background-color: rgb(from rgb(144, 202, 249) r g b / 0.1);
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
</style>
