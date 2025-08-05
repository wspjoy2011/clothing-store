<template>
  <div class="password-reset-confirm-page">
    <v-container class="password-reset-confirm-container">
      <v-row justify="center" align="center" class="min-height-screen">
        <v-col cols="12" sm="8" md="6" lg="4" xl="3">
          <div class="confirm-card-wrapper">
            <div class="floating-shapes">
              <div class="shape shape-1"></div>
              <div class="shape shape-2"></div>
              <div class="shape shape-3"></div>
              <div class="shape shape-4"></div>
            </div>

            <v-card
                elevation="12"
                class="confirm-card"
                :class="{ 'dark-theme': isDarkTheme }"
            >
              <v-card-title class="text-center pa-6 confirm-card-title" :class="{ 'dark-theme': isDarkTheme }">
                <v-icon size="48" color="primary" class="mb-4">mdi-key-change</v-icon>
                <h1 class="text-h4 font-weight-bold">Reset Password</h1>
                <p class="text-subtitle-1 text-medium-emphasis mt-2">
                  Enter your new password below
                </p>
              </v-card-title>

              <v-card-text class="pa-6">
                <!-- Success Message -->
                <PasswordResetConfirmStatusCard
                    v-if="confirmSuccess"
                    :success="true"
                    :message="'Password reset successful! You can now login with your new password.'"
                    :show-actions="true"
                    @go-to-login="goToLogin"
                />

                <!-- Error Message -->
                <v-alert
                    v-if="hasConfirmError"
                    type="error"
                    variant="tonal"
                    class="mb-6"
                    icon="mdi-alert-circle"
                >
                  <div class="text-subtitle-1 font-weight-medium">
                    {{ confirmErrorMessage }}
                  </div>
                </v-alert>

                <!-- Form -->
                <v-form
                    v-if="!confirmSuccess"
                    ref="confirmForm"
                    v-model="formValid"
                    @submit.prevent="handlePasswordResetConfirm"
                >
                  <v-text-field
                      v-model="password"
                      label="New Password"
                      :type="showPassword ? 'text' : 'password'"
                      variant="outlined"
                      density="comfortable"
                      prepend-inner-icon="mdi-lock"
                      :append-inner-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
                      :rules="passwordRules"
                      :disabled="isConfirming"
                      class="mb-4"
                      required
                      @click:append-inner="showPassword = !showPassword"
                  />

                  <v-text-field
                      v-model="confirmPassword"
                      label="Confirm New Password"
                      :type="showConfirmPassword ? 'text' : 'password'"
                      variant="outlined"
                      density="comfortable"
                      prepend-inner-icon="mdi-lock-check"
                      :append-inner-icon="showConfirmPassword ? 'mdi-eye' : 'mdi-eye-off'"
                      :rules="confirmPasswordRules"
                      :disabled="isConfirming"
                      class="mb-4"
                      required
                      @click:append-inner="showConfirmPassword = !showConfirmPassword"
                  />

                  <PasswordResetConfirmActions
                      :loading="isConfirming"
                      :disabled="!formValid || isConfirming"
                      @submit="handlePasswordResetConfirm"
                      @go-to-login="goToLogin"
                      @go-to-reset="goToPasswordReset"
                  />
                </v-form>
              </v-card-text>
            </v-card>

            <!-- Help Section -->
            <v-card
                elevation="2"
                class="mt-6 help-card"
                :class="{ 'dark-theme': isDarkTheme }"
            >
              <v-card-text class="pa-4">
                <v-row>
                  <v-col cols="12" md="6">
                    <div class="text-center">
                      <v-icon size="32" color="info" class="mb-2">mdi-shield-lock</v-icon>
                      <h3 class="text-h6 mb-2">Secure Reset</h3>
                      <p class="text-body-2 text-medium-emphasis">
                        Your password is encrypted and securely stored.
                      </p>
                    </div>
                  </v-col>
                  <v-col cols="12" md="6">
                    <div class="text-center">
                      <v-icon size="32" color="warning" class="mb-2">mdi-clock-alert</v-icon>
                      <h3 class="text-h6 mb-2">Link Expires</h3>
                      <p class="text-body-2 text-medium-emphasis">
                        Reset links expire after 24 hours for security.
                      </p>
                    </div>
                  </v-col>
                </v-row>
              </v-card-text>
            </v-card>
          </div>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script setup>
import {usePasswordResetConfirmPage} from '@/composables/accounts/usePasswordResetConfirmPage'
import PasswordResetConfirmStatusCard from '@/components/accounts/PasswordResetConfirmStatusCard.vue'
import PasswordResetConfirmActions from '@/components/accounts/PasswordResetConfirmActions.vue'

const props = defineProps({
  token: {
    type: String,
    default: ''
  }
})

const {
  isDarkTheme,
  password,
  confirmPassword,
  showPassword,
  showConfirmPassword,
  passwordRules,
  confirmPasswordRules,
  formValid,
  confirmForm,
  isConfirming,
  hasConfirmError,
  confirmErrorMessage,
  confirmSuccess,
  handlePasswordResetConfirm,
  goToLogin,
  goToPasswordReset
} = usePasswordResetConfirmPage(props)
</script>

<style scoped>
.password-reset-confirm-page {
  width: 100%;
}

.password-reset-confirm-container {
  min-height: calc(100vh - 64px);
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  position: relative;
}

.min-height-screen {
  min-height: calc(100vh - 104px);
}

.confirm-card-wrapper {
  position: relative;
  z-index: 2;
}

.floating-shapes {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
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
  top: 10%;
  left: 10%;
  animation-delay: 0s;
}

.shape-2 {
  width: 60px;
  height: 60px;
  top: 20%;
  right: 15%;
  animation-delay: 1s;
}

.shape-3 {
  width: 100px;
  height: 100px;
  bottom: 20%;
  left: 15%;
  animation-delay: 2s;
}

.shape-4 {
  width: 40px;
  height: 40px;
  bottom: 10%;
  right: 20%;
  animation-delay: 3s;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px) rotate(0deg);
  }
  33% {
    transform: translateY(-20px) rotate(120deg);
  }
  66% {
    transform: translateY(10px) rotate(240deg);
  }
}

.confirm-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 24px;
  overflow: hidden;
  transition: all 0.3s ease;
  animation: slideInUp 0.6s ease-out;
}

.confirm-card.dark-theme {
  background: rgba(30, 30, 30, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.confirm-card-title {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
}

.confirm-card-title.dark-theme {
  background: linear-gradient(135deg, #2d3748 0%, #4a5568 100%);
}

.help-card {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 16px;
}

.help-card.dark-theme {
  background: rgba(30, 30, 30, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(50px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 600px) {
  .password-reset-confirm-container {
    padding: 10px;
  }

  .confirm-card-title {
    padding: 24px 16px !important;
  }

  .confirm-card .v-card-text {
    padding: 24px 16px !important;
  }
}

:deep(.v-theme--dark .password-reset-confirm-container) {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
}
</style>
