<template>
  <v-footer
    class="footer"
    elevation="2"
    app
  >
    <v-container>
      <v-row>
        <!-- Brand and About -->
        <v-col cols="12" md="6" class="d-flex flex-column justify-center">
          <div class="d-flex align-center">
            <v-icon icon="mdi-store" size="small" class="mr-2"></v-icon>
            <span class="text-body-1 font-weight-bold">StyleShop</span>
          </div>
          <p class="text-caption text-medium-emphasis my-2">
            Your ultimate destination for fashion inspiration and high quality clothing.
          </p>
        </v-col>

        <!-- Newsletter -->
        <v-col cols="12" md="6" class="d-flex align-center">
          <v-row>
            <v-col cols="12" md="8">
              <v-text-field
                density="compact"
                variant="outlined"
                label="Subscribe to our newsletter"
                append-inner-icon="mdi-email-outline"
                hide-details
              ></v-text-field>
            </v-col>
            <v-col cols="12" md="4" class="d-flex align-center">
              <v-btn color="primary" block>Subscribe</v-btn>
            </v-col>
          </v-row>
        </v-col>
      </v-row>

      <v-divider class="my-2"></v-divider>

      <!-- Copyright and Social -->
      <div class="d-flex flex-column flex-md-row justify-space-between align-center py-2">
        <p class="text-caption text-medium-emphasis mb-2 mb-md-0">
          &copy; {{ currentYear }} StyleShop. All rights reserved.
        </p>
        <div>
          <v-btn icon variant="text" density="comfortable" size="small" class="mr-1">
            <v-icon size="small">mdi-facebook</v-icon>
          </v-btn>
          <v-btn icon variant="text" density="comfortable" size="small" class="mr-1">
            <v-icon size="small">mdi-twitter</v-icon>
          </v-btn>
          <v-btn icon variant="text" density="comfortable" size="small" class="mr-1">
            <v-icon size="small">mdi-instagram</v-icon>
          </v-btn>
          <v-btn icon variant="text" density="comfortable" size="small">
            <v-icon size="small">mdi-pinterest</v-icon>
          </v-btn>
        </div>
      </div>
    </v-container>
  </v-footer>
</template>

<script setup>
import { computed } from 'vue';

const currentYear = computed(() => new Date().getFullYear());
</script>

<style scoped>
.footer {
  background: linear-gradient(145deg, #fdfbfb 0%, #ebedee 100%);
}
</style>
