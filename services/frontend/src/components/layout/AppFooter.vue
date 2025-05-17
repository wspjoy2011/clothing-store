<template>
  <v-footer class="footer" elevation="2" app :class="{ 'footer-dark': isDarkTheme }">
    <v-container class="py-4">
      <v-row class="align-center">
        <!-- Brand and About (hidden on small screens) -->
        <v-col cols="12" md="6" class="d-none d-md-flex flex-column justify-center align-md-start">
          <div class="d-flex align-center mb-2">
            <v-icon icon="mdi-store" size="small" class="mr-2"></v-icon>
            <span class="text-body-1 font-weight-bold">StyleShop</span>
          </div>
          <p class="text-caption text-medium-emphasis">
            Your ultimate destination for fashion inspiration and high-quality clothing.
          </p>
        </v-col>

        <!-- Newsletter (hidden on smaller screens) -->
        <v-col cols="12" md="6" class="d-none d-md-flex">
          <v-row align="center" class="justify-end">
            <v-col cols="8">
              <v-text-field
                density="compact"
                variant="outlined"
                label="Subscribe to our newsletter"
                append-inner-icon="mdi-email-outline"
                hide-details
              ></v-text-field>
            </v-col>
            <v-col cols="4">
              <v-btn color="primary" block>Subscribe</v-btn>
            </v-col>
          </v-row>
        </v-col>
      </v-row>

      <!-- Divider (hidden on very small screens) -->
      <v-divider class="my-4 d-none d-md-block"></v-divider>

      <!-- Copyright and Social -->
      <v-row class="justify-space-between align-center">
        <v-col cols="12" sm="6" class="text-center text-sm-start">
          <p class="text-caption text-medium-emphasis mb-0">
            &copy; {{ currentYear }} StyleShop. All rights reserved.
          </p>
        </v-col>
        <v-col cols="12" sm="6" class="d-flex justify-center justify-sm-end">
          <div class="social-icons">
            <v-btn icon variant="text" density="comfortable" size="small" class="mr-2">
              <v-icon size="small">mdi-facebook</v-icon>
            </v-btn>
            <v-btn icon variant="text" density="comfortable" size="small" class="mr-2">
              <v-icon size="small">mdi-twitter</v-icon>
            </v-btn>
            <v-btn icon variant="text" density="comfortable" size="small" class="mr-2">
              <v-icon size="small">mdi-instagram</v-icon>
            </v-btn>
            <v-btn icon variant="text" density="comfortable" size="small">
              <v-icon size="small">mdi-pinterest</v-icon>
            </v-btn>
          </div>
        </v-col>
      </v-row>
    </v-container>
  </v-footer>
</template>

<script setup>
import { computed } from 'vue';
import { useUserPreferencesStore } from '@/stores/userPreferences';

const currentYear = computed(() => new Date().getFullYear());
const preferencesStore = useUserPreferencesStore();
const isDarkTheme = computed(() => preferencesStore.theme === 'dark');
</script>

<style scoped>
.footer {
  background: linear-gradient(145deg, #fdfbfb 0%, #ebedee 100%);
}

.footer-dark {
  background: linear-gradient(145deg, #1a1a1a 0%, #2c2c2c 100%) !important;
}

.social-icons {
  display: flex;
  align-items: center;
}

@media (max-width: 600px) {
  .footer {
    padding: 8px 0;
  }
}

@media (max-width: 960px) {
  .footer {
    padding: 12px 0;
  }
}
</style>
