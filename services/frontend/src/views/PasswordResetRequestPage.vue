<template>
  <div class="password-reset-page">
    <v-container class="password-reset-container">
      <v-row justify="center" align="center" class="min-height-screen">
        <v-col cols="12" sm="8" md="6" lg="4" xl="3">
          <div class="reset-card-wrapper">
            <div class="floating-shapes">
              <div class="shape shape-1"></div>
              <div class="shape shape-2"></div>
              <div class="shape shape-3"></div>
              <div class="shape shape-4"></div>
            </div>

            <v-card
                elevation="12"
                class="reset-card"
                :class="{ 'dark-theme': isDarkTheme }"
            >
              <v-card-title class="text-center pa-6 reset-card-title" :class="{ 'dark-theme': isDarkTheme }">
                <v-icon size="48" color="primary" class="mb-4">mdi-lock-reset</v-icon>
                <h1 class="text-h4 font-weight-bold">Reset Password</h1>
                <p class="text-subtitle-1 text-medium-emphasis mt-2">
                  Enter your email address and we'll send you a password reset link
                </p>
              </v-card-title>

              <v-card-text class="pa-6">
                <!-- Success Message -->
                <v-alert
                    v-if="requestSuccess"
                    type="success"
                    variant="tonal"
                    class="mb-6"
                    icon="mdi-check-circle"
                >
                  <div class="text-subtitle-1 font-weight-medium">
                    Password reset email sent successfully!
                  </div>
                  <div class="text-body-2 mt-1">
                    If an account with that email exists, we've sent you a password reset link.
                  </div>
                </v-alert>

                <!-- Error Message -->
                <v-alert
                    v-if="hasRequestError"
                    type="error"
                    variant="tonal"
                    class="mb-6"
                    icon="mdi-alert-circle"
                >
                  <div class="text-subtitle-1 font-weight-medium">
                    {{ requestErrorMessage }}
                  </div>
                </v-alert>

                <!-- Form -->
                <v-form
                    v-if="!requestSuccess"
                    ref="resetForm"
                    v-model="formValid"
                    @submit.prevent="handlePasswordResetRequest"
                >
                  <v-text-field
                      v-model="email"
                      label="Email Address"
                      type="email"
                      variant="outlined"
                      density="comfortable"
                      prepend-inner-icon="mdi-email"
                      :rules="emailRules"
                      :disabled="isRequesting"
                      class="mb-4"
                      required
                      autocomplete="email"
                  />

                  <v-btn
                      type="submit"
                      color="primary"
                      size="large"
                      block
                      :loading="isRequesting"
                      :disabled="!formValid || isRequesting"
                      class="mb-4 action-btn"
                  >
                    <v-icon start>mdi-send</v-icon>
                    Send Reset Link
                  </v-btn>
                </v-form>

                <!-- Success Actions -->
                <div v-if="requestSuccess" class="text-center">
                  <v-btn
                      color="primary"
                      variant="outlined"
                      size="large"
                      class="action-btn"
                      @click="resetFormData"
                  >
                    <v-icon start>mdi-refresh</v-icon>
                    Send Another Email
                  </v-btn>
                </div>

                <!-- Additional Links -->
                <div v-if="!requestSuccess" class="text-center mt-6">
                  <v-row>
                    <v-col cols="6">
                      <v-btn
                          color="primary"
                          variant="text"
                          class="action-btn"
                          @click="goToLogin"
                      >
                        <v-icon start>mdi-arrow-left</v-icon>
                        Back to Login
                      </v-btn>
                    </v-col>
                    <v-col cols="6">
                      <v-btn
                          color="primary"
                          variant="text"
                          class="action-btn"
                          @click="goToRegister"
                      >
                        <v-icon start>mdi-account-plus</v-icon>
                        Register
                      </v-btn>
                    </v-col>
                  </v-row>
                </div>
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
                      <v-icon size="32" color="info" class="mb-2">mdi-help-circle</v-icon>
                      <h3 class="text-h6 mb-2">Need Help?</h3>
                      <p class="text-body-2 text-medium-emphasis">
                        If you're having trouble, check your spam folder or contact support.
                      </p>
                    </div>
                  </v-col>
                  <v-col cols="12" md="6">
                    <div class="text-center">
                      <v-icon size="32" color="warning" class="mb-2">mdi-clock</v-icon>
                      <h3 class="text-h6 mb-2">Token Expired?</h3>
                      <p class="text-body-2 text-medium-emphasis">
                        Reset links expire after 1 hour. Request a new one if needed.
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
import {usePasswordResetRequestPage} from '@/composables/accounts/usePasswordResetRequestPage'

const props = defineProps({
  email: {
    type: String,
    default: ''
  }
})

const {
  isDarkTheme,
  email,
  emailRules,
  formValid,
  resetForm,
  isRequesting,
  hasRequestError,
  requestErrorMessage,
  requestSuccess,
  handlePasswordResetRequest,
  resetFormData,
  goToLogin,
  goToRegister
} = usePasswordResetRequestPage(props)
</script>

<style scoped>
.password-reset-page {
  width: 100%;
}

.password-reset-container {
  min-height: calc(100vh - 64px);
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  position: relative;
}

.min-height-screen {
  min-height: calc(100vh - 104px);
}

.reset-card-wrapper {
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

.reset-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 24px;
  overflow: hidden;
  transition: all 0.3s ease;
  animation: slideInUp 0.6s ease-out;
}

.reset-card.dark-theme {
  background: rgba(30, 30, 30, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.reset-card-title {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
}

.reset-card-title.dark-theme {
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
  .password-reset-container {
    padding: 10px;
  }

  .reset-card-title {
    padding: 24px 16px !important;
  }

  .reset-card .v-card-text {
    padding: 24px 16px !important;
  }
}

:deep(.v-theme--dark .password-reset-container) {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
}
</style>
