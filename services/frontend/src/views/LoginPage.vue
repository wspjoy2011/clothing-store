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
                ></v-icon>
                <h1 class="login-title">Welcome Back</h1>
                <p class="login-subtitle">Sign in to your StyleShop account</p>
              </div>

              <v-card-text class="login-form-section">
                <!-- Social Login Section -->
                <div class="social-login-section mb-6">
                  <v-btn
                      variant="outlined"
                      block
                      size="large"
                      class="social-btn google-btn mb-2"
                      :disabled="isLoading || isSocialAuthLoading"
                      :loading="isSocialAuthLoading && socialAuthType === 'google'"
                      @click="onGoogleLogin"
                  >
                    <v-icon start icon="mdi-google"></v-icon>
                    {{
                      (isSocialAuthLoading && socialAuthType === 'google') ? 'Connecting...' : 'Continue with Google'
                    }}
                  </v-btn>

                  <!-- Facebook Login Component -->
                  <HFaceBookLogin
                      :app-id="facebookAppId"
                      scope="email,public_profile"
                      fields="id,name,email,first_name,last_name,birthday"
                      @onSuccess="onFacebookSuccess"
                      @onFailure="onFacebookError"
                      class="facebook-login-wrapper"
                      v-slot="fbLogin"
                  >
                    <v-btn
                        variant="outlined"
                        block
                        size="large"
                        class="social-btn facebook-btn"
                        :disabled="isLoading || isSocialAuthLoading"
                        :loading="isSocialAuthLoading && socialAuthType === 'facebook'"
                        @click="fbLogin.initFBLogin"
                    >
                      <v-icon start icon="mdi-facebook"></v-icon>
                      {{
                        (isSocialAuthLoading && socialAuthType === 'facebook') ? 'Connecting...' : 'Continue with Facebook'
                      }}
                    </v-btn>
                  </HFaceBookLogin>
                </div>

                <div class="divider-section">
                  <v-divider class="my-4"></v-divider>
                  <span class="divider-text">or sign in with email</span>
                </div>

                <!-- Email Login Form -->
                <v-form
                    ref="formRef"
                    v-model="isFormValid"
                    @submit.prevent="onLogin"
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
                        label="Password"
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
                        autocomplete="current-password"
                    ></v-text-field>
                  </div>

                  <div class="form-field-wrapper">
                    <v-btn
                        type="submit"
                        block
                        size="large"
                        color="primary"
                        class="login-btn"
                        :loading="isLoading"
                        :disabled="!isFormReady || isLoading || isSocialAuthLoading"
                        elevation="2"
                    >
                      <v-icon start icon="mdi-login"></v-icon>
                      {{ isLoading ? 'Signing In...' : 'Sign In' }}
                    </v-btn>
                  </div>

                  <!-- Action buttons for errors -->
                  <div v-if="showActionButtons" class="action-buttons-section">
                    <v-divider class="my-4"></v-divider>

                    <v-btn
                        v-if="needsActivation"
                        variant="outlined"
                        block
                        size="large"
                        color="warning"
                        class="action-btn mb-2"
                        :disabled="isLoading || isSocialAuthLoading"
                        @click="goToActivationPage"
                    >
                      <v-icon start icon="mdi-email-check"></v-icon>
                      Activate Account
                    </v-btn>

                    <v-btn
                        v-if="needsRegistration"
                        variant="outlined"
                        block
                        size="large"
                        color="success"
                        class="action-btn"
                        :disabled="isLoading || isSocialAuthLoading"
                        @click="goToRegistration"
                    >
                      <v-icon start icon="mdi-account-plus"></v-icon>
                      Create Account
                    </v-btn>
                  </div>
                </v-form>
              </v-card-text>

              <v-card-actions class="login-footer">
                <div class="footer-content">
                  <span class="register-text">Don't have an account?</span>
                  <v-btn
                      variant="text"
                      color="primary"
                      class="register-link"
                      :disabled="isLoading || isSocialAuthLoading"
                      @click="goToRegister"
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
      <v-snackbar
          v-model="showSuccessMessage"
          color="success"
          timeout="5000"
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

      <v-snackbar
          v-model="showErrorMessage"
          color="error"
          timeout="8000"
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

      <v-snackbar
          v-model="showWarningMessage"
          color="warning"
          timeout="6000"
          location="top"
      >
        <v-icon start icon="mdi-alert"></v-icon>
        {{ warningMessage }}
        <template v-slot:actions>
          <v-btn variant="text" @click="hideWarning">
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
        <v-icon start :icon="socialAuthType === 'google' ? 'mdi-google' : 'mdi-facebook'"></v-icon>
        {{ socialSuccessMessage }}
        <template v-slot:actions>
          <v-btn variant="text" @click="hideSocialSuccess">
            Close
          </v-btn>
        </template>
      </v-snackbar>
    </v-container>
  </div>
</template>

<script setup>
import {computed, onMounted, ref, watch} from 'vue'
import {useTheme} from 'vuetify'
import {useAccountStore} from '@/stores/accounts'
import {useNavigation} from '@/composables/accounts/useNavigation'
import {useNotifications} from '@/composables/accounts/useNotifications'

const theme = useTheme()
const accountStore = useAccountStore()

const {
  goToRegister,
  goToActivation,
  handleGoogleAuth,
  handleFacebookSuccess,
  handleFacebookError,
  HFaceBookLogin,
  goToHome
} = useNavigation()

const {
  showSuccessMessage,
  showErrorMessage,
  showWarningMessage,
  successMessage,
  errorMessage,
  warningMessage,
  showSuccess,
  showError,
  hideSuccess,
  hideError,
  hideWarning
} = useNotifications()

const isDarkTheme = computed(() => theme.global.current.value.dark)

const facebookAppId = import.meta.env.VITE_FACEBOOK_APP_ID || ''

const formRef = ref(null)
const isFormValid = ref(false)
const email = ref('')
const password = ref('')
const showPassword = ref(false)

const emailTouched = ref(false)
const passwordTouched = ref(false)

const isSocialAuthLoading = ref(false)
const socialAuthType = ref('')
const showSocialSuccessMessage = ref(false)
const socialSuccessMessage = ref('')

const isLoading = computed(() => accountStore.isLoggingIn)
const needsActivation = computed(() => accountStore.needsActivation)
const needsRegistration = computed(() => accountStore.needsRegistration)

const showActionButtons = computed(() => {
  return accountStore.hasLoginError && (needsActivation.value || needsRegistration.value)
})

const emailRules = [
  v => !!v || 'Email is required',
  v => /.+@.+\..+/.test(v) || 'Email must be valid'
]

const passwordRules = [
  v => !!v || 'Password is required',
  v => v.length >= 8 || 'Password must be at least 8 characters'
]

const emailError = computed(() => {
  if (!emailTouched.value || !email.value) return false
  return !emailRules.every(rule => rule(email.value) === true)
})

const emailErrorMessage = computed(() => {
  if (!emailError.value) return ''
  const failedRule = emailRules.find(rule => rule(email.value) !== true)
  return failedRule ? failedRule(email.value) : ''
})

const passwordError = computed(() => {
  if (!passwordTouched.value || !password.value) return false
  return !passwordRules.every(rule => rule(password.value) === true)
})

const passwordErrorMessage = computed(() => {
  if (!passwordError.value) return ''
  const failedRule = passwordRules.find(rule => rule(password.value) !== true)
  return failedRule ? failedRule(password.value) : ''
})

const isFormReady = computed(() => {
  return isFormValid.value &&
      email.value &&
      password.value &&
      !emailError.value &&
      !passwordError.value
})

const hideSocialSuccess = () => {
  showSocialSuccessMessage.value = false
  socialSuccessMessage.value = ''
  socialAuthType.value = ''
}

watch(() => accountStore.hasLoginError, (hasError) => {
  if (hasError && accountStore.loginErrorMessage) {
    showError(accountStore.loginErrorMessage)
  }
})

watch(() => accountStore.loginSuccess, (success) => {
  if (success) {
    showSuccess('Login successful! Welcome back.')
    setTimeout(() => {
      hideSuccess()
      goToHome()
    }, 1500)
  }
})

const onLogin = async () => {
  if (!isFormReady.value || isLoading.value) return

  accountStore.clearLoginState()

  const result = await accountStore.login({
    email: email.value,
    password: password.value
  })

  if (!result.success) {
    console.error('Login failed:', result.error)
  }
}

const goToActivationPage = () => {
  goToActivation(email.value)
}

const goToRegistration = () => {
  goToRegister()
}

const onGoogleLogin = async () => {
  isSocialAuthLoading.value = true
  socialAuthType.value = 'google'

  try {
    const result = await handleGoogleAuth(true)

    if (result && result.success) {
      if (result.isNewUser) {
        socialSuccessMessage.value = 'Welcome! Your Google account has been successfully registered and signed in.'
      } else {
        socialSuccessMessage.value = 'Welcome back! You have been signed in with your Google account.'
      }

      showSocialSuccessMessage.value = true

      setTimeout(() => {
        hideSocialSuccess()
        goToHome()
      }, 3000)

    } else if (result && result.error) {
      showError(result.message || 'Google login failed. Please try again.')
    } else {
      showError('Google login failed. Please try again.')
    }

  } catch (error) {
    console.error('Google login error:', error)
    showError('An unexpected error occurred during Google login.')
  } finally {
    isSocialAuthLoading.value = false
    socialAuthType.value = ''
  }
}

const onFacebookSuccess = async (response) => {
  isSocialAuthLoading.value = true
  socialAuthType.value = 'facebook'

  try {
    const result = await handleFacebookSuccess(response)

    if (result && result.success) {
      if (result.isNewUser) {
        socialSuccessMessage.value = 'Welcome! Your Facebook account has been successfully registered and signed in.'
      } else {
        socialSuccessMessage.value = 'Welcome back! You have been signed in with your Facebook account.'
      }

      showSocialSuccessMessage.value = true

      setTimeout(() => {
        hideSocialSuccess()
        goToHome()
      }, 3000)

    } else if (result && result.error) {
      showError(result.message || 'Facebook login failed. Please try again.')
    } else {
      showError('Facebook login failed. Please try again.')
    }

  } catch (error) {
    console.error('Facebook login error:', error)
    showError('An unexpected error occurred during Facebook login.')
  } finally {
    isSocialAuthLoading.value = false
    socialAuthType.value = ''
  }
}

const onFacebookError = (error) => {
  const result = handleFacebookError(error)

  if (result && result.error) {
    showError(result.message || 'Facebook login failed. Please try again.')
  } else {
    showError('Facebook login failed. Please try again.')
  }
}

onMounted(() => {
  document.title = 'StyleShop - Login'
})
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
  padding: 2rem 1rem;
}

.min-height-screen {
  min-height: 100vh;
}

.login-card-wrapper {
  position: relative;
  width: 100%;
}

.floating-shapes {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  z-index: 1;
  pointer-events: none;
}

.shape {
  position: absolute;
  opacity: 0.1;
  animation: float 15s ease-in-out infinite;
}

.shape-1 {
  top: 10%;
  left: 10%;
  width: 60px;
  height: 60px;
  background: linear-gradient(45deg, #ff6b6b, #ee5a24);
  border-radius: 50%;
  animation-delay: 0s;
}

.shape-2 {
  top: 60%;
  right: 10%;
  width: 80px;
  height: 80px;
  background: linear-gradient(45deg, #4ecdc4, #44bd87);
  border-radius: 20px;
  animation-delay: 5s;
}

.shape-3 {
  bottom: 20%;
  left: 20%;
  width: 40px;
  height: 40px;
  background: linear-gradient(45deg, #45b7d1, #4285f4);
  border-radius: 50%;
  animation-delay: 10s;
}

.shape-4 {
  top: 30%;
  right: 30%;
  width: 50px;
  height: 50px;
  background: linear-gradient(45deg, #f093fb, #f5576c);
  border-radius: 15px;
  animation-delay: 7s;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px) rotate(0deg);
  }
  50% {
    transform: translateY(-20px) rotate(180deg);
  }
}

.login-card {
  position: relative;
  z-index: 2;
  backdrop-filter: blur(10px);
  background: rgba(255, 255, 255, 0.95);
  border-radius: 24px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  overflow: hidden;
  animation: fadeInUp 0.6s ease-out;
}

.login-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.15);
}

.login-card.dark-theme {
  background: rgba(30, 30, 30, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.login-header {
  text-align: center;
  padding: 2rem 2rem 1rem;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
}

.login-icon {
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
}

.login-title {
  font-size: 2rem;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea, #764ba2);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 0.5rem;
}

.login-subtitle {
  color: #666;
  font-size: 1rem;
  margin: 0;
}

.dark-theme .login-subtitle {
  color: #ccc;
}

.login-form-section {
  padding: 32px;
}

.form-field-wrapper {
  margin-bottom: 1.5rem;
  position: relative;
}

.animated-field {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.animated-field:focus-within {
  transform: translateY(-2px);
}

.login-btn {
  height: 56px;
  border-radius: 16px;
  font-weight: 600;
  text-transform: none;
  font-size: 1.1rem;
  transition: all 0.3s ease;
  background: linear-gradient(135deg, #667eea, #764ba2);
}

.login-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
}

.login-btn:disabled {
  transform: none;
}

.action-buttons-section {
  margin: 1rem 0;
}

.action-btn {
  height: 48px;
  border-radius: 12px;
  font-weight: 600;
  text-transform: none;
  transition: all 0.3s ease;
}

.action-btn:hover {
  transform: translateY(-1px);
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
  border-radius: 12px;
  font-weight: 600;
  text-transform: none;
  transition: all 0.3s ease;
  border: 2px solid rgba(0, 0, 0, 0.12);
}

.social-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.social-btn:disabled {
  opacity: 0.6;
  transform: none;
}

.social-btn .v-btn__loader {
  color: inherit;
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

.facebook-login-wrapper {
  width: 100%;
}

.login-footer {
  padding: 1rem 2rem 2rem;
  justify-content: center;
}

.footer-content {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.register-text {
  color: #666;
  font-size: 0.9rem;
}

.dark-theme .register-text {
  color: #ccc;
}

.register-link {
  font-weight: 600;
  text-transform: none;
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

@media (max-width: 600px) {
  .login-container {
    padding: 1rem 0.5rem;
  }

  .login-header {
    padding: 1.5rem 1rem 0.5rem;
  }

  .login-title {
    font-size: 1.5rem;
  }

  .login-form-section {
    padding: 24px 16px;
  }

  .login-footer {
    padding: 16px;
  }

  .form-field-wrapper {
    margin-bottom: 20px;
  }

  .floating-shapes {
    display: none;
  }
}

@media (max-width: 768px) {
  .login-page {
    overflow-y: auto;
  }

  .login-page::-webkit-scrollbar {
    width: 4px;
  }

  .login-page::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.1);
  }

  .login-page::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.3);
    border-radius: 2px;
  }
}
</style>
