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
                        :disabled="isLoading"
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
                        :disabled="isLoading"
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
                        :disabled="!isFormReady || isLoading"
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
                        :disabled="isLoading"
                        @click="goToActivation"
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
                        :disabled="isLoading"
                        @click="goToRegistration"
                    >
                      <v-icon start icon="mdi-account-plus"></v-icon>
                      Create Account
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
                        @click="handleGoogleLogin"
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
                        @click="handleFacebookLogin"
                    >
                      <v-icon start icon="mdi-facebook"></v-icon>
                      Continue with Facebook
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
                      :disabled="isLoading"
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

      <v-snackbar
          v-model="showSuccessMessage"
          color="success"
          timeout="5000"
          location="top"
      >
        <v-icon start icon="mdi-check-circle"></v-icon>
        Login successful! Welcome back.
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
    </v-container>
  </div>
</template>

<script setup>
import {computed, ref, watch} from 'vue'
import {useTheme} from 'vuetify'
import {useRouter} from 'vue-router'
import {useAccountStore} from '@/stores/accounts'

const theme = useTheme()
const router = useRouter()
const accountStore = useAccountStore()

const isDarkTheme = computed(() => theme.global.current.value.dark)

const formRef = ref(null)
const isFormValid = ref(false)
const email = ref('')
const password = ref('')
const showPassword = ref(false)

const emailTouched = ref(false)
const passwordTouched = ref(false)

const showSuccessMessage = ref(false)
const showErrorMessage = ref(false)

const isLoading = computed(() => accountStore.isLoggingIn)
const errorMessage = computed(() => accountStore.loginErrorMessage)
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

// Field validation
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

watch(() => accountStore.hasLoginError, (hasError) => {
  if (hasError) {
    showErrorMessage.value = true
  }
})

watch(() => accountStore.loginSuccess, (success) => {
  if (success) {
    showSuccessMessage.value = true
    setTimeout(() => {
      router.push({name: 'home'})
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

const goToActivation = () => {
  router.push({
    name: 'activate',
    query: {email: email.value}
  })
}

const goToRegistration = () => {
  router.push({name: 'register'})
}

const goToRegister = () => {
  router.push({name: 'register'})
}

const hideSuccess = () => {
  showSuccessMessage.value = false
}

const hideError = () => {
  showErrorMessage.value = false
  accountStore.clearLoginState()
}

const handleGoogleLogin = () => {
  console.log('Google login clicked')
}

const handleFacebookLogin = () => {
  console.log('Facebook login clicked')
}
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
}

.login-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.15);
}

.login-card.dark-theme {
  background: rgba(30, 30, 30, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.1);
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
  padding: 1rem 2rem;
}

.form-field-wrapper {
  margin-bottom: 1.5rem;
  position: relative;
}

.animated-field {
  transition: all 0.3s ease;
}

.animated-field:hover {
  transform: translateY(-1px);
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
  margin: 2rem 0;
}

.divider-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: rgba(255, 255, 255, 0.95);
  padding: 0 1rem;
  color: #666;
  font-size: 0.9rem;
}

.dark-theme .divider-text {
  background: rgba(30, 30, 30, 0.95);
  color: #ccc;
}

.social-login-section {
  margin: 1rem 0;
}

.social-btn {
  height: 48px;
  border-radius: 12px;
  font-weight: 600;
  text-transform: none;
  transition: all 0.3s ease;
}

.social-btn:hover {
  transform: translateY(-1px);
}

.google-btn:hover {
  background-color: rgba(66, 133, 244, 0.1);
  border-color: #4285f4;
}

.facebook-btn:hover {
  background-color: rgba(24, 119, 242, 0.1);
  border-color: #1877f2;
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
    padding: 0.5rem 1rem;
  }

  .login-footer {
    padding: 0.5rem 1rem 1.5rem;
  }

  .form-field-wrapper {
    margin-bottom: 1rem;
  }
}

.login-card {
  animation: fadeInUp 0.6s ease-out;
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
</style>
