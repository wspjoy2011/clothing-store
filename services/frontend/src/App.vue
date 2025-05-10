<template>
  <v-app>
    <app-header />

    <v-main class="main-content">
      <router-view />
    </v-main>

    <app-footer />
  </v-app>
</template>

<script setup>
import AppHeader from '@/components/layout/AppHeader.vue';
import AppFooter from '@/components/layout/AppFooter.vue';
</script>

<style>
.main-content {
  min-height: calc(100vh - 180px);
}
</style>
