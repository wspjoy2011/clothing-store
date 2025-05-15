<template>
  <v-btn
    icon
    variant="text"
    @click="toggleTheme"
  >
    <v-icon>{{ isDarkTheme ? 'mdi-weather-sunny' : 'mdi-weather-night' }}</v-icon>
  </v-btn>
</template>

<script setup>
import { computed } from 'vue';
import { useTheme } from 'vuetify';
import { useUserPreferencesStore } from '@/stores/userPreferences';

const theme = useTheme();
const preferencesStore = useUserPreferencesStore();

const isDarkTheme = computed(() => preferencesStore.theme === 'dark');

function toggleTheme() {
  const newTheme = isDarkTheme.value ? 'light' : 'dark';
  preferencesStore.setTheme(newTheme);
  theme.global.name.value = newTheme;
}
</script>
