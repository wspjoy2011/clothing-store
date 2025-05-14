<template>
  <v-footer
    class="footer"
    elevation="2"
    app
  >
    <v-container>
      <v-row>
        <!-- Brand and About - disappears on medium and smaller screens -->
        <v-col cols="12" lg="4" class="d-none d-lg-flex flex-column justify-center">
          <div class="d-flex align-center">
            <v-icon icon="mdi-store" size="small" class="mr-2"></v-icon>
            <span class="text-body-1 font-weight-bold">StyleShop</span>
          </div>
          <p class="text-caption text-medium-emphasis my-2">
            Your ultimate destination for fashion inspiration and high quality clothing.
          </p>
        </v-col>

        <!-- Newsletter - disappears on large screens except for xl and larger -->
        <v-col cols="12" xl="8" class="d-none d-xl-flex align-center">
          <v-row>
            <v-col cols="12" xl="8">
              <v-text-field
                density="compact"
                variant="outlined"
                label="Subscribe to our newsletter"
                append-inner-icon="mdi-email-outline"
                hide-details
              ></v-text-field>
            </v-col>
            <v-col cols="12" xl="4" class="d-flex align-center">
              <v-btn color="primary" block>Subscribe</v-btn>
            </v-col>
          </v-row>
        </v-col>
      </v-row>

      <!-- Divider - only shows when there's content above it -->
      <v-divider class="my-2 d-none d-lg-block"></v-divider>

      <!-- Copyright and Social - always visible but becomes more compact -->
      <div class="d-flex flex-column flex-md-row justify-space-between align-center py-2">
        <p class="text-caption text-medium-emphasis mb-2 mb-md-0">
          &copy; {{ currentYear }} StyleShop. All rights reserved.
        </p>
        <div class="social-icons">
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

:deep(.v-container) {
  padding-top: 8px;
  padding-bottom: 8px;
}

/* Further reduce footer height on small and medium screens */
@media (max-width: 1264px) {
  .footer {
    padding: 4px 0;
  }

  :deep(.v-container) {
    padding-top: 8px;
    padding-bottom: 8px;
  }

  .social-icons {
    display: flex;
    margin-top: 0;
  }
}

/* Extra compact for small screens but with better spacing */
@media (max-width: 600px) {
  .footer {
    padding: 8px 0;
  }

  :deep(.v-container) {
    padding-top: 12px;
    padding-bottom: 12px;
  }

  /* Wrapper for copyright and social icons */
  .d-flex.flex-column {
    padding-top: 4px;
  }

  .social-icons {
    justify-content: center;
    margin-top: 8px;
  }

  /* Add some space between copyright text and the edge */
  .text-caption {
    margin-left: 4px;
    margin-right: 4px;
  }
}

</style>
