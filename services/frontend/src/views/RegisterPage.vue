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
                <!-- Social Login Section -->
                <div class="social-login-section mb-6">
                  <v-btn
                      variant="outlined"
                      block
                      size="large"
                      class="social-btn google-btn mb-2"
                      :disabled="isLoading || isSocialAuthLoading"
                      :loading="isSocialAuthLoading"
                      @click="onGoogleRegister"
                  >
                    <v-icon start icon="mdi-google"></v-icon>
                    {{ isSocialAuthLoading ? 'Connecting...' : 'Continue with Google' }}
                  </v-btn>

                  <v-btn
                      variant="outlined"
                      block
                      size="large"
                      class="social-btn facebook-btn"
                      :disabled="isLoading || isSocialAuthLoading"
                      @click="onFacebookRegister"
                  >
                    <v-icon start icon="mdi-facebook"></v-icon>
                    Continue with Facebook
                  </v-btn>
                </div>

                <div class="divider-section">
                  <v-divider class="my-4"></v-divider>
                  <span class="divider-text">or create with email</span>
                </div>

                <!-- Local Registration Form -->
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
                        :disabled="isLoading || isSocialAuthLoading"
                        color="primary"
                        clearable
                        validate-on="input lazy"
                        :error="emailTouched && emailError"
                        :error-messages="emailTouched && emailError ? emailErrorMessage : ''"
                        @focus="emailTouched = true"
                        autocomplete="email"
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
                        :disabled="isLoading || isSocialAuthLoading"
                        color="primary"
                        validate-on="input lazy"
                        :error="passwordTouched && passwordError"
                        :error-messages="passwordTouched && passwordError ? passwordErrorMessage : ''"
                        @focus="passwordTouched = true"
                        autocomplete="new-password"
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
                        :disabled="isLoading || isSocialAuthLoading"
                        color="primary"
                        validate-on="input lazy"
                        :error="confirmPasswordTouched && confirmPasswordError"
                        :error-messages="confirmPasswordTouched && confirmPasswordError ? confirmPasswordErrorMessage : ''"
                        @focus="confirmPasswordTouched = true"
                        autocomplete="new-password"
                    ></v-text-field>
                  </div>

                  <div class="form-field-wrapper">
                    <v-checkbox
                        v-model="acceptTerms"
                        :rules="termsRules"
                        color="primary"
                        :disabled="isLoading || isSocialAuthLoading"
                        validate-on="input lazy"
                        :readonly="!legalStore.hasReadBothDocuments"
                        @click="handleCheckboxClick"
                    >
                      <template v-slot:label>
                        <span class="terms-text">
                          I agree to the
                          <a href="#" class="terms-link" @click.prevent="openTerms">
                            Terms of Service
                            <v-chip
                                v-if="legalStore.termsAccepted"
                                size="x-small"
                                color="success"
                                variant="tonal"
                                class="ml-1"
                            >
                              ✓
                            </v-chip>
                          </a>
                          and
                          <a href="#" class="terms-link" @click.prevent="openPrivacy">
                            Privacy Policy
                            <v-chip
                                v-if="legalStore.privacyAcknowledged"
                                size="x-small"
                                color="success"
                                variant="tonal"
                                class="ml-1"
                            >
                              ✓
                            </v-chip>
                          </a>
                        </span>
                      </template>
                    </v-checkbox>

                    <div v-if="!legalStore.hasReadBothDocuments" class="terms-requirement-hint">
                      <v-chip size="small" color="info" variant="tonal">
                        <v-icon start size="small">mdi-information</v-icon>
                        Please read both documents first
                      </v-chip>
                    </div>
                  </div>

                  <div class="form-field-wrapper">
                    <v-btn
                        type="submit"
                        block
                        size="large"
                        color="primary"
                        class="register-btn"
                        :loading="isLoading"
                        :disabled="!isFormReady || isLoading || isSocialAuthLoading"
                        elevation="2"
                    >
                      <v-icon start icon="mdi-account-plus"></v-icon>
                      {{ isLoading ? 'Creating Account...' : 'Create Account' }}
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
                      :disabled="isLoading || isSocialAuthLoading"
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

      <!-- Success Messages -->
      <v-snackbar
          v-model="showSuccessMessage"
          color="success"
          timeout="6000"
          location="top"
      >
        <v-icon start icon="mdi-check-circle"></v-icon>
        {{ successMessage }}
        <template v-slot:actions>
          <v-btn variant="text" @click="hideSuccess">
            Close
          </v-btn>
        </template>
      </v-snackbar>

      <!-- Error Messages -->
      <v-snackbar
          v-model="showErrorMessage"
          color="error"
          timeout="7000"
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

      <!-- Social Auth Success -->
      <v-snackbar
          v-model="showSocialSuccessMessage"
          color="success"
          timeout="6000"
          location="top"
      >
        <v-icon start icon="mdi-google"></v-icon>
        {{ socialSuccessMessage }}
        <template v-slot:actions>
          <v-btn variant="text" @click="hideSocialSuccess">
            Close
          </v-btn>
        </template>
      </v-snackbar>
    </v-container>

    <TermsOfService
        v-model="legalStore.showTermsDialog"
        @accept="handleTermsAccept"
    />

    <PrivacyPolicy
        v-model="legalStore.showPrivacyDialog"
        @acknowledge="handlePrivacyAcknowledge"
    />
  </div>
</template>

<script setup>
import {computed, onMounted, ref} from 'vue'
import {useTheme} from 'vuetify'
import {useRegistrationForm} from '@/composables/accounts/useRegistrationForm'
import {useNotifications} from '@/composables/accounts/useNotifications'
import {useNavigation} from '@/composables/accounts/useNavigation'
import {useLegalStore} from '@/stores/legal'
import TermsOfService from '@/components/modals/TermsOfService.vue'
import PrivacyPolicy from '@/components/modals/PrivacyPolicy.vue'

const theme = useTheme()
const isDarkTheme = computed(() => theme.global.current.value.dark)
const legalStore = useLegalStore()

const isSocialAuthLoading = ref(false)
const showSocialSuccessMessage = ref(false)
const socialSuccessMessage = ref('')

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
  successMessage,
  showSuccess,
  showError,
  hideSuccess,
  hideError
} = useNotifications()

const {
  goToLogin,
  handleGoogleAuth,
  handleFacebookAuth,
  openTerms,
  openPrivacy,
  handleTermsAccept,
  handlePrivacyAcknowledge,
  goToHome
} = useNavigation()

const handleCheckboxClick = (event) => {
  if (!legalStore.hasReadBothDocuments) {
    event.preventDefault()
    return false
  }
}

const hideSocialSuccess = () => {
  showSocialSuccessMessage.value = false
  socialSuccessMessage.value = ''
}

const onGoogleRegister = async () => {
  isSocialAuthLoading.value = true

  try {
    const result = await handleGoogleAuth(false)

    if (result && result.success) {
      if (result.isNewUser) {
        socialSuccessMessage.value = 'Welcome! Your Google account has been successfully registered.'
      } else {
        socialSuccessMessage.value = 'Welcome back! You have been signed in with your existing Google account.'
      }

      showSocialSuccessMessage.value = true

      setTimeout(() => {
        hideSocialSuccess()
        goToHome()
      }, 4000)

    } else if (result && result.error) {
      showError(result.message || 'Google registration failed. Please try again.')
    } else {
      showError('Google registration failed. Please try again.')
    }

  } catch (error) {
    console.error('Google registration error:', error)
    showError('An unexpected error occurred during Google registration.')
  } finally {
    isSocialAuthLoading.value = false
  }
}

const onFacebookRegister = async () => {
  handleFacebookAuth(false)
}

const onRegister = async () => {
  const result = await handleRegister()

  if (result && result.success) {
    showSuccess('Account created successfully! Please check your email for verification.')
    resetForm()

    setTimeout(() => {
      hideSuccess()
      goToLogin()
    }, 4000)

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
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
  overflow: hidden;
}

.register-container {
  position: relative;
  z-index: 2;
  padding: 2rem 1rem;
}

.min-height-screen {
  min-height: 100vh;
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
  font-size: 2rem;
  font-weight: 700;
  margin: 0;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.register-subtitle {
  font-size: 1rem;
  opacity: 0.9;
  margin: 8px 0 0;
}

.register-form-section {
  padding: 32px;
}

.form-field-wrapper {
  margin-bottom: 24px;
}

.animated-field {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.animated-field:focus-within {
  transform: translateY(-2px);
}

.terms-text {
  font-size: 0.875rem;
  line-height: 1.5;
}

.terms-link {
  color: #1976D2;
  text-decoration: none;
  font-weight: 500;
  transition: opacity 0.2s ease;
}

.terms-link:hover {
  opacity: 0.8;
  text-decoration: underline;
}

.terms-requirement-hint {
  margin-top: 8px;
  margin-left: 32px;
}

.register-btn {
  height: 56px;
  font-weight: 600;
  text-transform: none;
  letter-spacing: 0.5px;
  border-radius: 12px;
  transition: all 0.3s ease;
}

.register-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(25, 118, 210, 0.3) !important;
}

.register-btn:disabled {
  transform: none;
}

.divider-section {
  position: relative;
  text-align: center;
  margin: 32px 0;
}

.divider-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: rgba(255, 255, 255, 0.95);
  padding: 0 16px;
  font-size: 0.875rem;
  color: rgba(0, 0, 0, 0.6);
  font-weight: 500;
}

.dark-theme .divider-text {
  background: rgba(30, 30, 30, 0.95);
  color: rgba(255, 255, 255, 0.7);
}

.social-login-section {
  margin-bottom: 24px;
}

.social-btn {
  height: 48px;
  font-weight: 500;
  text-transform: none;
  border-radius: 12px;
  transition: all 0.3s ease;
  border: 2px solid rgba(0, 0, 0, 0.12);
}

.social-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.google-btn {
  color: #4285f4;
  border-color: #4285f4;
}

.google-btn:hover {
  background-color: rgba(66, 133, 244, 0.04);
  border-color: #4285f4;
}

.facebook-btn {
  color: #1877f2;
  border-color: #1877f2;
}

.facebook-btn:hover {
  background-color: rgba(24, 119, 242, 0.04);
  border-color: #1877f2;
}

.register-footer {
  padding: 16px 32px 32px;
  justify-content: center;
}

.footer-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.login-text {
  font-size: 0.875rem;
  color: rgba(0, 0, 0, 0.6);
}

.dark-theme .login-text {
  color: rgba(255, 255, 255, 0.7);
}

.login-link {
  font-weight: 600;
  text-transform: none;
  padding: 4px 8px;
  min-width: auto;
  height: auto;
}

@media (max-width: 600px) {
  .register-container {
    padding: 1rem 0.5rem;
  }

  .register-form-section {
    padding: 24px 16px;
  }

  .register-footer {
    padding: 16px;
  }

  .register-title {
    font-size: 1.75rem;
  }

  .register-subtitle {
    font-size: 0.875rem;
  }

  .form-field-wrapper {
    margin-bottom: 20px;
  }

  .floating-shapes {
    display: none;
  }
}

.social-btn:disabled {
  opacity: 0.6;
  transform: none;
}

.social-btn .v-btn__loader {
  color: inherit;
}

.v-field--error {
  animation: shake 0.5s ease-in-out;
}

@keyframes shake {
  0%, 100% {
    transform: translateX(0);
  }
  25% {
    transform: translateX(-4px);
  }
  75% {
    transform: translateX(4px);
  }
}

@media (max-width: 768px) {
  .register-page {
    overflow-y: auto;
  }

  .register-page::-webkit-scrollbar {
    width: 4px;
  }

  .register-page::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.1);
  }

  .register-page::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.3);
    border-radius: 2px;
  }
}
</style>
