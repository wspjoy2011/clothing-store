<template>
  <v-app-bar
    app
    elevation="2"
    class="header"
  >
    <v-container class="d-flex align-center">
      <!-- Logo and Brand Name -->
      <div class="d-flex align-center">
        <v-icon icon="mdi-store" size="large" class="mr-2"></v-icon>
        <span class="text-h5 font-weight-bold">StyleShop</span>
      </div>

      <!-- Navigation Menu -->
      <v-tabs
        v-model="activeTab"
        class="ml-6 hidden-sm-and-down"
      >
        <v-tab :to="{ name: 'home' }" value="home">Home</v-tab>
        <v-tab :to="{ name: 'catalog' }" value="catalog">Catalog</v-tab>
        <v-tab value="new">New Arrivals</v-tab>
        <v-tab value="sale">Sale</v-tab>
      </v-tabs>

      <v-spacer></v-spacer>

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
    </v-list>
  </v-navigation-drawer>
</template>

<script setup>
import { ref } from 'vue';

const activeTab = ref('home');
const drawer = ref(false);
</script>

<style scoped>
.header {
  background: linear-gradient(145deg, #fdfbfb 0%, #ebedee 100%);
}
</style>