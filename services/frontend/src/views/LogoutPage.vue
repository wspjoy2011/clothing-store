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
              <div class="logout-header">
                <v-icon
                    :icon="getStatusIcon"
                    :color="getStatusColor"
                    size="64"
                    class="logout-icon mb-4"
                ></v-icon>
                <h1 class="logout-title">{{ getStatusTitle }}</h1>
                <p class="logout-subtitle">{{ getStatusSubtitle }}</p>
              </div>

              <v-card-text class="logout-content">
                <!-- Loading State -->
                <div v-if="isLoading" class="loading-section">
                  <v-progress-circular
                      indeterminate
                      color="primary"
                      size="64"
                      class="mb-4"
                  ></v-progress-circular>
                  <p class="text-body-1">Signing you out...</p>
                </div>

                <!-- Success State -->
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

                <!-- Error State -->
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

              <v-card-actions class="logout-actions">
                <div class="action-buttons">
                  <v-btn
                      color="primary"
                      variant="elevated"
                      block
                      size="large"
                      @click="goToHome"
                      :disabled="isLoading"
                  >
                    <v-icon start icon="mdi-home"></v-icon>
                    Go to Home
                  </v-btn>

                  <div class="secondary-actions mt-3">
                    <v-btn
                        variant="outlined"
                        color="primary"
                        block
                        @click="goToLogin"
                        :disabled="isLoading"
                    >
                      <v-icon start icon="mdi-login"></v-icon>
                      Sign In Again
                    </v-btn>
                  </div>
                </div>
              </v-card-actions>
            </v-card>
          </div>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script setup>
import {computed, onMounted, ref} from 'vue'
import {useTheme} from 'vuetify'
import {useAccountStore} from '@/stores/accounts'
import {useNavigation} from '@/composables/accounts/useNavigation'

const theme = useTheme()
const accountStore = useAccountStore()
const {goToHome, goToLogin} = useNavigation()

const isDarkTheme = computed(() => theme.global.current.value.dark)

const isLoading = ref(true)
const logoutSuccess = ref(false)
const logoutError = ref(null)
const logoutWarning = ref(null)

const getStatusIcon = computed(() => {
  if (isLoading.value) return 'mdi-loading'
  if (logoutSuccess.value) return 'mdi-check-circle'
  if (logoutError.value) return 'mdi-alert-circle'
  return 'mdi-logout'
})

const getStatusColor = computed(() => {
  if (isLoading.value) return 'primary'
  if (logoutSuccess.value) return 'success'
  if (logoutError.value) return 'error'
  return 'primary'
})

const getStatusTitle = computed(() => {
  if (isLoading.value) return 'Signing Out'
  if (logoutSuccess.value) return 'You have been successfully logged out'
  if (logoutError.value) return 'Logout Error'
  return 'Logout'
})

const getStatusSubtitle = computed(() => {
  if (isLoading.value) return 'Please wait while we sign you out...'
  if (logoutSuccess.value) return 'Your session has been safely terminated'
  if (logoutError.value) return 'There was an issue, but you are logged out locally'
  return 'Logout process'
})

onMounted(async () => {
  try {
    await new Promise(resolve => setTimeout(resolve, 1000))

    const result = await accountStore.logout()

    if (result.success) {
      logoutSuccess.value = true

      if (result.warning) {
        logoutWarning.value = result.warning
      }

      console.log('User logged out successfully')
    } else {
      logoutError.value = result.message || 'Failed to logout'
    }
  } catch (error) {
    console.error('Logout error:', error)
    logoutError.value = 'Network error occurred during logout'

    accountStore.clearLocalState()
  } finally {
    isLoading.value = false
  }
})
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

.logout-header {
  text-align: center;
  padding: 2rem 2rem 1rem;
}

.logout-title {
  font-size: 1.75rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: rgba(0, 0, 0, 0.87);
}

.dark-theme .logout-title {
  color: rgba(255, 255, 255, 0.87);
}

.logout-subtitle {
  color: rgba(0, 0, 0, 0.6);
  font-size: 1rem;
  margin: 0;
}

.dark-theme .logout-subtitle {
  color: rgba(255, 255, 255, 0.6);
}

.logout-content {
  padding: 1rem 2rem;
}

.loading-section,
.success-section,
.error-section {
  text-align: center;
}

.logout-actions {
  padding: 1rem 2rem 2rem;
}

.action-buttons {
  width: 100%;
}

.secondary-actions {
  display: flex;
  gap: 0.5rem;
}

.secondary-actions .v-btn {
  flex: 1;
}

@media (max-width: 600px) {
  .logout-card {
    margin: 1rem;
    border-radius: 16px;
  }

  .logout-header {
    padding: 1.5rem 1.5rem 1rem;
  }

  .logout-content {
    padding: 1rem 1.5rem;
  }

  .logout-actions {
    padding: 1rem 1.5rem 1.5rem;
  }

  .secondary-actions {
    flex-direction: column;
    gap: 0.75rem;
  }

  .secondary-actions .v-btn {
    flex: none;
  }
}
</style>
