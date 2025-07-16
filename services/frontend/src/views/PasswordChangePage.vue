<template>
  <div class="password-change-page">
    <v-container class="password-change-container">
      <v-row justify="center" align="center" class="min-height-screen">
        <v-col cols="12" sm="8" md="6" lg="4" xl="3">
          <div class="change-card-wrapper">
            <div class="floating-shapes">
              <div class="shape shape-1"></div>
              <div class="shape shape-2"></div>
              <div class="shape shape-3"></div>
              <div class="shape shape-4"></div>
            </div>

            <v-card
                elevation="12"
                class="change-card"
                :class="{ 'dark-theme': isDarkTheme }"
            >
              <v-card-title class="text-center pa-6 change-card-title" :class="{ 'dark-theme': isDarkTheme }">
                <v-icon size="48" color="primary" class="mb-4">mdi-shield-key</v-icon>
                <h1 class="text-h4 font-weight-bold">Change Password</h1>
                <p class="text-subtitle-1 text-medium-emphasis mt-2">
                  Update your account password
                </p>
              </v-card-title>

              <v-card-text class="pa-6">
                <!-- Success Message -->
                <v-alert
                    v-if="changeSuccess"
                    type="success"
                    variant="tonal"
                    class="mb-6"
                    icon="mdi-check-circle"
                >
                  <div class="text-subtitle-1 font-weight-medium">
                    Password changed successfully!
                  </div>
                  <div class="text-body-2 mt-1">
                    Your password has been updated. Please keep it secure.
                  </div>
                </v-alert>

                <!-- Error Message -->
                <v-alert
                    v-if="hasChangeError"
                    type="error"
                    variant="tonal"
                    class="mb-6"
                    icon="mdi-alert-circle"
                >
                  <div class="text-subtitle-1 font-weight-medium">
                    {{ changeErrorMessage }}
                  </div>
                </v-alert>

                <!-- Form -->
                <v-form
                    v-if="!changeSuccess"
                    ref="changeForm"
                    v-model="formValid"
                    @submit.prevent="handlePasswordChange"
                >
                  <!-- Hidden username field for accessibility -->
                  <input
                      type="text"
                      name="username"
                      :value="userEmail"
                      autocomplete="username"
                      style="display: none;"
                      readonly
                  />

                  <v-text-field
                      v-model="oldPassword"
                      label="Current Password"
                      :type="showOldPassword ? 'text' : 'password'"
                      variant="outlined"
                      density="comfortable"
                      prepend-inner-icon="mdi-lock"
                      :append-inner-icon="showOldPassword ? 'mdi-eye' : 'mdi-eye-off'"
                      :rules="oldPasswordRules"
                      :disabled="isChanging"
                      class="mb-4"
                      required
                      autocomplete="current-password"
                      @click:append-inner="showOldPassword = !showOldPassword"
                  />

                  <v-text-field
                      v-model="newPassword"
                      label="New Password"
                      :type="showNewPassword ? 'text' : 'password'"
                      variant="outlined"
                      density="comfortable"
                      prepend-inner-icon="mdi-lock-plus"
                      :append-inner-icon="showNewPassword ? 'mdi-eye' : 'mdi-eye-off'"
                      :rules="newPasswordRules"
                      :disabled="isChanging"
                      class="mb-4"
                      required
                      autocomplete="new-password"
                      @click:append-inner="showNewPassword = !showNewPassword"
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
                      :disabled="isChanging"
                      class="mb-4"
                      required
                      autocomplete="new-password"
                      @click:append-inner="showConfirmPassword = !showConfirmPassword"
                  />

                  <v-btn
                      type="submit"
                      color="primary"
                      size="large"
                      block
                      :loading="isChanging"
                      :disabled="!formValid || isChanging"
                      class="mb-4 action-btn"
                  >
                    <v-icon start>mdi-shield-check</v-icon>
                    Change Password
                  </v-btn>
                </v-form>

                <!-- Success Actions -->
                <div v-if="changeSuccess" class="text-center">
                  <v-btn
                      color="primary"
                      variant="outlined"
                      size="large"
                      class="action-btn mb-3"
                      @click="goToProfile"
                  >
                    <v-icon start>mdi-account</v-icon>
                    Go to Profile
                  </v-btn>
                  <v-btn
                      color="secondary"
                      variant="text"
                      size="large"
                      class="action-btn"
                      @click="resetForm"
                  >
                    <v-icon start>mdi-refresh</v-icon>
                    Change Again
                  </v-btn>
                </div>

                <!-- Additional Links -->
                <div v-if="!changeSuccess" class="text-center mt-6">
                  <v-btn
                      color="secondary"
                      variant="text"
                      class="action-btn"
                      @click="goToHome"
                  >
                    <v-icon start>mdi-home</v-icon>
                    Back to Home
                  </v-btn>
                </div>
              </v-card-text>
            </v-card>

            <!-- Security Tips -->
            <v-card
                elevation="2"
                class="mt-6 help-card"
                :class="{ 'dark-theme': isDarkTheme }"
            >
              <v-card-text class="pa-4">
                <v-row>
                  <v-col cols="12" md="4">
                    <div class="text-center">
                      <v-icon size="32" color="success" class="mb-2">mdi-shield-check</v-icon>
                      <h3 class="text-h6 mb-2">Strong Password</h3>
                      <p class="text-body-2 text-medium-emphasis">
                        Use at least 8 characters with mixed case, numbers, and symbols.
                      </p>
                    </div>
                  </v-col>
                  <v-col cols="12" md="4">
                    <div class="text-center">
                      <v-icon size="32" color="warning" class="mb-2">mdi-security</v-icon>
                      <h3 class="text-h6 mb-2">Keep It Secure</h3>
                      <p class="text-body-2 text-medium-emphasis">
                        Never share your password and change it regularly.
                      </p>
                    </div>
                  </v-col>
                  <v-col cols="12" md="4">
                    <div class="text-center">
                      <v-icon size="32" color="info" class="mb-2">mdi-email-alert</v-icon>
                      <h3 class="text-h6 mb-2">Email Notification</h3>
                      <p class="text-body-2 text-medium-emphasis">
                        You'll receive a confirmation email after changing your password.
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
import {usePasswordChangePage} from '@/composables/accounts/usePasswordChangePage'

const {
  isDarkTheme,
  userEmail,
  oldPassword,
  newPassword,
  confirmPassword,
  showOldPassword,
  showNewPassword,
  showConfirmPassword,
  oldPasswordRules,
  newPasswordRules,
  confirmPasswordRules,
  formValid,
  changeForm,
  isChanging,
  hasChangeError,
  changeErrorMessage,
  changeSuccess,
  handlePasswordChange,
  resetForm,
  goToProfile,
  goToHome
} = usePasswordChangePage()
</script>

<style scoped>
.password-change-page {
  width: 100%;
}

.password-change-container {
  min-height: calc(100vh - 64px);
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  position: relative;
}

.min-height-screen {
  min-height: calc(100vh - 104px);
}

.change-card-wrapper {
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

.change-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 24px;
  overflow: hidden;
  transition: all 0.3s ease;
  animation: slideInUp 0.6s ease-out;
}

.change-card.dark-theme {
  background: rgba(30, 30, 30, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.change-card-title {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
}

.change-card-title.dark-theme {
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

.action-btn {
  border-radius: 12px;
  font-weight: 600;
  text-transform: none;
  letter-spacing: 0.025em;
  transition: all 0.3s ease;
}

.action-btn:hover {
  transform: translateY(-2px);
}

@media (max-width: 600px) {
  .password-change-container {
    padding: 10px;
  }

  .change-card-title {
    padding: 24px 16px !important;
  }

  .change-card .v-card-text {
    padding: 24px 16px !important;
  }
}

:deep(.v-theme--dark .password-change-container) {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
}
</style>
