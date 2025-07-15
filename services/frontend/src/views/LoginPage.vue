<template>
  <div class="login-page">
    <v-container class="login-container">
      <v-row justify="center" align="center" class="min-height-screen">
        <v-col cols="12" sm="8" md="6" lg="4" xl="3">
          <div class="login-card-wrapper">
            <div class="floating-shapes">
              <div class="shape shape-1"></div>
              <div class="shape shape-2"></div>
              <div class="shape shape-3"></div>
              <div class="shape shape-4"></div>
            </div>

            <v-card
                class="login-card elevation-12"
                :class="{ 'dark-theme': isDarkTheme }"
            >
              <div class="login-header">
                <v-icon
                    icon="mdi-login"
                    size="48"
                    class="login-icon mb-3"
                    color="primary"
                />
                <h1 class="login-title">Welcome Back</h1>
                <p class="login-subtitle">Sign in to your StyleShop account</p>
              </div>

              <v-card-text class="login-form-section">
                <!-- Social Login Section -->
                <social-login
                    :facebook-app-id="facebookAppId"
                    :is-loading="isLoading"
                    :is-social-auth-loading="isSocialAuthLoading"
                    :social-auth-type="socialAuthType"
                    @google-login="handleGoogleLogin"
                    @facebook-success="handleFacebookSuccess"
                    @facebook-error="handleFacebookError"
                />

                <div class="divider-section">
                  <v-divider class="my-4" />
                  <span class="divider-text">or sign in with email</span>
                </div>

                <!-- Email Login Form -->
                <login-form
                    :is-loading="isLoading"
                    :is-social-auth-loading="isSocialAuthLoading"
                    :needs-activation="needsActivation"
                    :needs-registration="needsRegistration"
                    :show-action-buttons="showActionButtons"
                    :login-error="formLoginError"
                    :show-login-error="showFormLoginError"
                    @submit="handleEmailLogin"
                    @activate="handleActivation"
                    @register="handleRegistration"
                    @clear-login-error="handleClearLoginError"
                    @forgot-password="handleForgotPassword"
                />
              </v-card-text>

              <v-card-actions class="login-footer">
                <div class="footer-content">
                  <span class="register-text">Don't have an account?</span>
                  <v-btn
                      variant="text"
                      color="primary"
                      class="register-link"
                      :disabled="isLoading || isSocialAuthLoading"
                      @click="handleRegisterClick"
                  >
                    Sign Up
                  </v-btn>
                </div>
              </v-card-actions>
            </v-card>
          </div>
        </v-col>
      </v-row>

      <!-- Notifications -->
      <login-snackbar
          :show-success-message="showSuccessMessage"
          :show-error-message="showErrorMessage"
          :show-warning-message="showWarningMessage"
          :show-social-success-message="showSocialSuccessMessage"
          :success-message="successMessage"
          :error-message="errorMessage"
          :warning-message="warningMessage"
          :social-success-message="socialSuccessMessage"
          :social-auth-type="socialAuthType"
          @hide-success="hideSuccess"
          @hide-error="hideError"
          @hide-warning="hideWarning"
          @hide-social-success="hideSocialSuccess"
      />
    </v-container>
  </div>
</template>

<script setup>
import {useLoginPage} from '@/composables/accounts/useLoginPage';

import SocialLogin from '@/components/accounts/SocialLogin.vue';
import LoginForm from '@/components/accounts/LoginForm.vue';
import LoginSnackbar from '@/components/accounts/LoginSnackbar.vue';

const {
  // Theme
  isDarkTheme,

  // Configuration
  facebookAppId,

  // Auth state
  isLoading,
  isSocialAuthLoading,
  socialAuthType,
  needsActivation,
  needsRegistration,
  showActionButtons,

  // Notifications state
  showSuccessMessage,
  showErrorMessage,
  showWarningMessage,
  successMessage,
  errorMessage,
  warningMessage,
  showSocialSuccessMessage,
  socialSuccessMessage,

  // Form error state
  formLoginError,
  showFormLoginError,

  // Notification handlers
  hideSuccess,
  hideError,
  hideWarning,
  hideSocialSuccess,

  // Auth handlers
  handleEmailLogin,
  handleGoogleLogin,
  handleFacebookSuccess,
  handleFacebookError,
  handleActivation,
  handleRegistration,
  handleRegisterClick,
  handleForgotPassword,
  handleClearLoginError
} = useLoginPage();
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
  overflow: hidden;
}

.login-container {
  position: relative;
  z-index: 2;
}

.min-height-screen {
  min-height: 100vh;
}

.login-card-wrapper {
  position: relative;
  z-index: 1;
}

.floating-shapes {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  z-index: 0;
}

.shape {
  position: absolute;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  animation: float 15s infinite ease-in-out;
}

.shape-1 {
  width: 100px;
  height: 100px;
  top: 10%;
  left: 10%;
  animation-delay: 0s;
}

.shape-2 {
  width: 150px;
  height: 150px;
  top: 60%;
  right: 10%;
  animation-delay: 5s;
}

.shape-3 {
  width: 80px;
  height: 80px;
  bottom: 20%;
  left: 20%;
  animation-delay: 10s;
}

.shape-4 {
  width: 120px;
  height: 120px;
  top: 30%;
  right: 30%;
  animation-delay: 2s;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px) rotate(0deg);
    opacity: 0.5;
  }
  50% {
    transform: translateY(-20px) rotate(180deg);
    opacity: 0.8;
  }
}

.login-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 32px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
}

.login-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
}

.dark-theme {
  background: rgba(30, 30, 30, 0.95) !important;
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.login-icon {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
  100% {
    transform: scale(1);
  }
}

.login-title {
  font-size: 28px;
  font-weight: 700;
  color: #333;
  margin-bottom: 8px;
}

.dark-theme .login-title {
  color: #ffffff;
}

.login-subtitle {
  font-size: 16px;
  color: #666;
  margin: 0;
}

.dark-theme .login-subtitle {
  color: #cccccc;
}

.login-form-section {
  padding: 0 8px;
}

.divider-section {
  position: relative;
  text-align: center;
  margin: 24px 0;
}

.divider-text {
  background: rgba(255, 255, 255, 0.95);
  padding: 0 16px;
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.dark-theme .divider-text {
  background: rgba(30, 30, 30, 0.95);
  color: #cccccc;
}

.login-footer {
  padding: 24px 8px 8px;
  justify-content: center;
}

.footer-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.register-text {
  font-size: 14px;
  color: #666;
}

.dark-theme .register-text {
  color: #cccccc;
}

.register-link {
  font-weight: 600;
  text-transform: none;
  padding: 4px 8px;
  min-width: auto;
}

@media (max-width: 600px) {
  .login-card {
    padding: 24px 16px;
    border-radius: 16px;
  }

  .login-title {
    font-size: 24px;
  }

  .login-subtitle {
    font-size: 14px;
  }

  .shape {
    display: none;
  }
}
</style>
