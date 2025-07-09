<template>
  <div class="logout-page">
    <v-container class="logout-container">
      <v-row justify="center" align="center" class="min-height-screen">
        <v-col cols="12" sm="8" md="6" lg="4" xl="3">
          <div class="logout-card-wrapper">
            <div class="floating-shapes">
              <div class="shape shape-1"></div>
              <div class="shape shape-2"></div>
              <div class="shape shape-3"></div>
            </div>

            <v-card
                class="logout-card elevation-12"
                :class="{ 'dark-theme': isDarkTheme }"
            >
              <logout-status-icon
                  :is-loading="isLoading"
                  :logout-success="logoutSuccess"
                  :logout-error="logoutError"
                  :is-dark-theme="isDarkTheme"
              />

              <v-card-text class="logout-content">
                <div v-if="isLoading" class="loading-section">
                  <v-progress-circular
                      indeterminate
                      color="primary"
                      size="64"
                      class="mb-4"
                  ></v-progress-circular>
                  <p class="text-body-1">Signing you out...</p>
                </div>

                <div v-else-if="logoutSuccess" class="success-section">
                  <v-alert
                      type="success"
                      variant="tonal"
                      class="mb-4"
                  >
                    Logout completed successfully
                  </v-alert>

                  <div v-if="logoutWarning" class="warning-section">
                    <v-alert
                        type="warning"
                        variant="tonal"
                        class="mb-4"
                    >
                      <v-icon start icon="mdi-alert"></v-icon>
                      {{ logoutWarning }}
                    </v-alert>
                  </div>

                  <p class="text-body-2 text-center">
                    Thank you for using StyleShop. You can now safely close this page or continue browsing.
                  </p>
                </div>

                <div v-else-if="logoutError" class="error-section">
                  <v-alert
                      type="error"
                      variant="tonal"
                      class="mb-4"
                  >
                    <v-icon start icon="mdi-alert-circle"></v-icon>
                    {{ logoutError }}
                  </v-alert>

                  <p class="text-body-2 text-center mb-4">
                    Don't worry, you have been logged out locally for security.
                  </p>
                </div>
              </v-card-text>

              <logout-actions
                  :is-loading="isLoading"
                  @go-home="goToHome"
                  @go-login="goToLogin"
              />
            </v-card>
          </div>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script setup>
import {useLogoutPage} from '@/composables/accounts/useLogoutPage';
import LogoutStatusIcon from '@/components/accounts/LogoutStatusIcon.vue';
import LogoutActions from '@/components/accounts/LogoutActions.vue';

const {
  isDarkTheme,
  isLoading,
  logoutSuccess,
  logoutError,
  logoutWarning,
  goToHome,
  goToLogin
} = useLogoutPage();
</script>

<style scoped>
.logout-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
  overflow: hidden;
}

.logout-container {
  position: relative;
  z-index: 2;
}

.min-height-screen {
  min-height: 100vh;
}

.logout-card-wrapper {
  position: relative;
  perspective: 1000px;
}

.floating-shapes {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  z-index: 1;
}

.shape {
  position: absolute;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  animation: float 6s ease-in-out infinite;
}

.shape-1 {
  width: 80px;
  height: 80px;
  top: -40px;
  left: -40px;
  animation-delay: 0s;
}

.shape-2 {
  width: 60px;
  height: 60px;
  top: 50%;
  right: -30px;
  animation-delay: 2s;
}

.shape-3 {
  width: 100px;
  height: 100px;
  bottom: -50px;
  left: 50%;
  animation-delay: 4s;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px) rotate(0deg);
  }
  50% {
    transform: translateY(-20px) rotate(180deg);
  }
}

.logout-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  position: relative;
  z-index: 2;
  animation: slideUp 0.8s ease-out;
}

.logout-card.dark-theme {
  background: rgba(33, 33, 33, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.logout-content {
  padding: 1rem 2rem;
}

.loading-section,
.success-section,
.error-section {
  text-align: center;
}

:deep(.dark-theme .logout-title) {
  color: rgba(255, 255, 255, 0.87);
}

:deep(.dark-theme .logout-subtitle) {
  color: rgba(255, 255, 255, 0.6);
}

@media (max-width: 600px) {
  .logout-card {
    margin: 1rem;
    border-radius: 16px;
  }

  .logout-content {
    padding: 1rem 1.5rem;
  }
}
</style>
