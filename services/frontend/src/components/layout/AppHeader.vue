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

        <!-- Navigation Menu - Centered -->
        <div class="hidden-sm-and-down nav-center">
          <v-tabs
              v-model="activeTab"
              centered
          >
            <v-tab :to="{ name: 'home' }" value="home">Home</v-tab>
            <v-tab :to="{ name: 'catalog' }" value="catalog">Catalog</v-tab>
            <v-tab value="new">New Arrivals</v-tab>
            <v-tab value="sale">Sale</v-tab>
          </v-tabs>
        </div>

        <!-- Right Side Icons -->
        <div class="d-flex align-center">
          <!-- Theme Toggle -->
          <theme-toggle class="mr-2"/>

          <!-- Search Button -->
          <v-btn icon class="mr-2">
            <v-icon>mdi-magnify</v-icon>
          </v-btn>

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
      <v-list-item title="Home" value="home" prepend-icon="mdi-home"></v-list-item>
      <v-list-item title="Catalog" value="catalog" prepend-icon="mdi-view-grid"></v-list-item>
      <v-list-item title="New Arrivals" value="new" prepend-icon="mdi-star"></v-list-item>
      <v-list-item title="Sale" value="sale" prepend-icon="mdi-tag"></v-list-item>
      <v-divider></v-divider>
      <v-list-item title="My Account" value="account" prepend-icon="mdi-account"></v-list-item>
      <v-list-item title="Shopping Cart" value="cart" prepend-icon="mdi-cart"></v-list-item>
      <!-- Add theme toggle to mobile menu too -->
      <v-list-item title="Toggle Theme" @click="toggleTheme" prepend-icon="mdi-theme-light-dark"></v-list-item>
    </v-list>
  </v-navigation-drawer>
</template>

<script setup>
import {ref} from 'vue';
import {useTheme} from 'vuetify';
import ThemeToggle from '@/components/ui/theme/ThemeToggle.vue';
import {useUserPreferencesStore} from '@/stores/userPreferences';

const activeTab = ref('home');
const drawer = ref(false);
const theme = useTheme();
const preferencesStore = useUserPreferencesStore();

function toggleTheme() {
  const newTheme = preferencesStore.theme === 'dark' ? 'light' : 'dark';
  preferencesStore.setTheme(newTheme);
  theme.global.name.value = newTheme;
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
</style>
