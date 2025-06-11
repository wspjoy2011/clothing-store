<template>
  <div class="register-page">
    <v-container class="register-container">
      <v-row justify="center" align="center" class="min-height-screen">
        <v-col cols="12" sm="8" md="6" lg="4" xl="3">
          <div class="register-card-wrapper">
            <div class="floating-shapes">
              <div class="shape shape-1"></div>
              <div class="shape shape-2"></div>
              <div class="shape shape-3"></div>
              <div class="shape shape-4"></div>
            </div>

            <v-card
                class="register-card elevation-12"
                :class="{ 'dark-theme': isDarkTheme }"
            >
              <div class="register-header">
                <v-icon
                    icon="mdi-account-plus"
                    size="48"
                    class="register-icon mb-3"
                    color="primary"
                ></v-icon>
                <h1 class="register-title">Join StyleShop</h1>
                <p class="register-subtitle">Create your account to start shopping</p>
              </div>

              <v-card-text class="register-form-section">
                <v-form
                    ref="formRef"
                    v-model="isFormValid"
                    @submit.prevent="onRegister"
                    validate-on="input lazy"
                    fast-fail
                >
                  <div class="form-field-wrapper">
                    <v-text-field
                        v-model="email"
                        label="Email Address"
                        type="email"
                        variant="outlined"
                        :rules="emailRules"
                        prepend-inner-icon="mdi-email-outline"
                        class="animated-field"
                        :loading="isLoading"
                        :disabled="isLoading"
                        color="primary"
                        clearable
                        validate-on="input lazy"
                        :error="emailTouched && emailError"
                        :error-messages="emailTouched && emailError ? emailErrorMessage : ''"
                        @focus="emailTouched = true"
                    ></v-text-field>
                  </div>

                  <div class="form-field-wrapper">
                    <v-text-field
                        v-model="password"
                        :label="passwordFieldLabel"
                        :type="showPassword ? 'text' : 'password'"
                        variant="outlined"
                        :rules="passwordRules"
                        prepend-inner-icon="mdi-lock-outline"
                        :append-inner-icon="showPassword ? 'mdi-eye-off' : 'mdi-eye'"
                        @click:append-inner="showPassword = !showPassword"
                        class="animated-field"
                        :loading="isLoading"
                        :disabled="isLoading"
                        color="primary"
                        validate-on="input lazy"
                        :error="passwordTouched && passwordError"
                        :error-messages="passwordTouched && passwordError ? passwordErrorMessage : ''"
                        @focus="passwordTouched = true"
                    ></v-text-field>
                  </div>

                  <div class="form-field-wrapper">
                    <v-text-field
                        v-model="confirmPassword"
                        label="Confirm Password"
                        :type="showConfirmPassword ? 'text' : 'password'"
                        variant="outlined"
                        :rules="confirmPasswordRules"
                        prepend-inner-icon="mdi-lock-check-outline"
                        :append-inner-icon="showConfirmPassword ? 'mdi-eye-off' : 'mdi-eye'"
                        @click:append-inner="showConfirmPassword = !showConfirmPassword"
                        class="animated-field"
                        :loading="isLoading"
                        :disabled="isLoading"
                        color="primary"
                        validate-on="input lazy"
                        :error="confirmPasswordTouched && confirmPasswordError"
                        :error-messages="confirmPasswordTouched && confirmPasswordError ? confirmPasswordErrorMessage : ''"
                        @focus="confirmPasswordTouched = true"
                    ></v-text-field>
                  </div>

                  <div class="form-field-wrapper">
                    <v-checkbox
                        v-model="acceptTerms"
                        :rules="termsRules"
                        color="primary"
                        :disabled="isLoading"
                        validate-on="input lazy"
                    >
                      <template v-slot:label>
                        <span class="terms-text">
                          I agree to the
                          <a href="#" class="terms-link" @click.prevent="openTerms">Terms of Service</a>
                          and
                          <a href="#" class="terms-link" @click.prevent="openPrivacy">Privacy Policy</a>
                        </span>
                      </template>
                    </v-checkbox>
                  </div>

                  <div class="form-field-wrapper">
                    <v-btn
                        type="submit"
                        block
                        size="large"
                        color="primary"
                        class="register-btn"
                        :loading="isLoading"
                        :disabled="!isFormReady || isLoading"
                        elevation="2"
                    >
                      <v-icon start icon="mdi-account-plus"></v-icon>
                      {{ isLoading ? 'Creating Account...' : 'Create Account' }}
                    </v-btn>
                  </div>

                  <div class="divider-section">
                    <v-divider class="my-4"></v-divider>
                    <span class="divider-text">or</span>
                  </div>

                  <div class="social-login-section">
                    <v-btn
                        variant="outlined"
                        block
                        size="large"
                        class="social-btn google-btn mb-2"
                        :disabled="isLoading"
                        @click="handleGoogleRegister"
                    >
                      <v-icon start icon="mdi-google"></v-icon>
                      Continue with Google
                    </v-btn>

                    <v-btn
                        variant="outlined"
                        block
                        size="large"
                        class="social-btn facebook-btn"
                        :disabled="isLoading"
                        @click="handleFacebookRegister"
                    >
                      <v-icon start icon="mdi-facebook"></v-icon>
                      Continue with Facebook
                    </v-btn>
                  </div>
                </v-form>
              </v-card-text>

              <v-card-actions class="register-footer">
                <div class="footer-content">
                  <span class="login-text">Already have an account?</span>
                  <v-btn
                      variant="text"
                      color="primary"
                      class="login-link"
                      :disabled="isLoading"
                      @click="goToLogin"
                  >
                    Sign In
                  </v-btn>
                </div>
              </v-card-actions>
            </v-card>
          </div>
        </v-col>
      </v-row>

      <v-snackbar
          v-model="showSuccessMessage"
          color="success"
          timeout="5000"
          location="top"
      >
        <v-icon start icon="mdi-check-circle"></v-icon>
        Account created successfully! Please check your email for verification.
        <template v-slot:actions>
          <v-btn variant="text" @click="hideSuccess">
            Close
          </v-btn>
        </template>
      </v-snackbar>

      <v-snackbar
          v-model="showErrorMessage"
          color="error"
          timeout="5000"
          location="top"
      >
        <v-icon start icon="mdi-alert-circle"></v-icon>
        {{ errorMessage }}
        <template v-slot:actions>
          <v-btn variant="text" @click="hideError">
            Close
          </v-btn>
        </template>
      </v-snackbar>
    </v-container>
  </div>
</template>

<script setup>
import {computed, onMounted} from 'vue'
import {useTheme} from 'vuetify'
import {useRegistrationForm} from '@/composables/accounts/useRegistrationForm'
import {useNotifications} from '@/composables/accounts/useNotifications'
import {useNavigation} from '@/composables/accounts/useNavigation'

const theme = useTheme()
const isDarkTheme = computed(() => theme.global.current.value.dark)

const {
  formRef,
  isFormValid,
  email,
  password,
  confirmPassword,
  acceptTerms,
  showPassword,
  showConfirmPassword,
  isLoading,
  passwordFieldLabel,
  isFormReady,
  emailRules,
  passwordRules,
  confirmPasswordRules,
  termsRules,
  resetForm,
  handleRegister,
  emailTouched,
  passwordTouched,
  confirmPasswordTouched,
  emailError,
  passwordError,
  confirmPasswordError,
  emailErrorMessage,
  passwordErrorMessage,
  confirmPasswordErrorMessage
} = useRegistrationForm()

const {
  showSuccessMessage,
  showErrorMessage,
  errorMessage,
  showSuccess,
  showError,
  hideSuccess,
  hideError
} = useNotifications()

const {
  goToLogin,
  handleGoogleRegister,
  handleFacebookRegister,
  openTerms,
  openPrivacy
} = useNavigation()

const onRegister = async () => {
  const result = await handleRegister()

  if (result && result.success) {
    showSuccess()
    resetForm()
    setTimeout(() => {
      goToLogin()
    }, 2000)
  } else if (result && result.error) {
    showError(result.error)
  } else {
    showError('Registration failed. Please try again.')
  }
}

onMounted(() => {
  document.title = 'StyleShop - Register'
})
</script>

<style scoped>
.register-page {
  width: 100%;
}

.register-container {
  min-height: calc(100vh - 64px);
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  position: relative;
}

.min-height-screen {
  min-height: calc(100vh - 104px);
}

.register-card-wrapper {
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

.register-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 24px;
  overflow: hidden;
  transition: all 0.3s ease;
  animation: slideInUp 0.6s ease-out;
}

.register-card.dark-theme {
  background: rgba(30, 30, 30, 0.95);
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

.register-header {
  text-align: center;
  padding: 32px 24px 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  position: relative;
}

.register-icon {
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

.register-title {
  font-size: 1.75rem;
  font-weight: 600;
  margin: 0;
  letter-spacing: -0.025em;
}

.register-subtitle {
  font-size: 0.95rem;
  opacity: 0.9;
  margin: 8px 0 0;
}

.register-form-section {
  padding: 32px 24px 16px;
}

.form-field-wrapper {
  margin-bottom: 20px;
}

.animated-field {
  transition: all 0.3s ease;
}

.animated-field:hover {
  transform: translateY(-2px);
}

.terms-text {
  font-size: 0.875rem;
  line-height: 1.4;
}

.terms-link {
  color: #667eea;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s ease;
}

.terms-link:hover {
  color: #764ba2;
  text-decoration: underline;
}

.register-btn {
  border-radius: 12px;
  font-weight: 600;
  text-transform: none;
  letter-spacing: 0.025em;
  transition: all 0.3s ease;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.register-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
}

.register-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.divider-section {
  position: relative;
  margin: 24px 0;
}

.divider-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: white;
  padding: 0 16px;
  color: #666;
  font-size: 0.875rem;
}

.dark-theme .divider-text {
  background: #1e1e1e;
  color: #ccc;
}

.social-login-section {
  margin-bottom: 8px;
}

.social-btn {
  border-radius: 12px;
  text-transform: none;
  font-weight: 500;
  transition: all 0.3s ease;
  border: 2px solid #e0e0e0;
}

.social-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.google-btn:hover {
  border-color: #4285f4;
  color: #4285f4;
}

.facebook-btn:hover {
  border-color: #1877f2;
  color: #1877f2;
}

.register-footer {
  padding: 16px 24px 24px;
  background: rgba(248, 249, 250, 0.8);
  border-top: 1px solid rgba(0, 0, 0, 0.05);
}

.dark-theme .register-footer {
  background: rgba(40, 40, 40, 0.8);
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.footer-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
}

.login-text {
  font-size: 0.875rem;
  color: #666;
}

.dark-theme .login-text {
  color: #ccc;
}

.login-link {
  text-transform: none;
  font-weight: 600;
  padding: 4px 8px;
}

@media (max-width: 600px) {
  .register-container {
    padding: 10px;
  }

  .register-form-section {
    padding: 24px 16px 16px;
  }

  .register-header {
    padding: 24px 16px 16px;
  }

  .register-title {
    font-size: 1.5rem;
  }

  .form-field-wrapper {
    margin-bottom: 16px;
  }
}

:deep(.v-theme--dark .register-container) {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
}

:deep(.v-theme--dark .v-text-field .v-field) {
  background: rgba(255, 255, 255, 0.05);
}

:deep(.v-theme--dark .v-checkbox .v-selection-control__input) {
  color: #90caf9;
}
</style>
