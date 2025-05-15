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
import { onMounted } from 'vue';
import { useTheme } from 'vuetify';
import { useUserPreferencesStore } from '@/stores/userPreferences';

import AppHeader from '@/components/layout/AppHeader.vue';
import AppFooter from '@/components/layout/AppFooter.vue';

const theme = useTheme();
const preferencesStore = useUserPreferencesStore();

onMounted(() => {
  theme.global.name.value = preferencesStore.theme;
});

</script>

<style>
.main-content {
  min-height: calc(100vh - 180px);
}
</style>
