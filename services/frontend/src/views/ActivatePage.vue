<template>
  <div class="activate-page">
    <v-container class="activate-container">
      <v-row justify="center" align="center" class="min-height-screen">
        <v-col cols="12" sm="8" md="6" lg="4" xl="3">
          <div class="activate-card-wrapper">
            <div class="floating-shapes">
              <div class="shape shape-1"></div>
              <div class="shape shape-2"></div>
              <div class="shape shape-3"></div>
              <div class="shape shape-4"></div>
            </div>

            <v-card
                class="activate-card elevation-12"
                :class="{ 'dark-theme': isDarkTheme }"
            >
              <!-- Loading State -->
              <div v-if="isLoading" class="activate-loading">
                <div class="loading-content">
                  <v-progress-circular
                      indeterminate
                      size="64"
                      color="primary"
                      class="mb-4"
                  ></v-progress-circular>
                  <h2 class="loading-title">Activating Account</h2>
                  <p class="loading-subtitle">Please wait while we activate your account...</p>
                </div>
              </div>

              <!-- Success State -->
              <div v-else-if="activationSuccess" class="activate-success">
                <div class="success-content">
                  <v-icon
                      icon="mdi-check-circle"
                      size="64"
                      color="success"
                      class="success-icon mb-4"
                  ></v-icon>
                  <h2 class="success-title">Account Activated!</h2>
                  <p class="success-subtitle">
                    Your account has been successfully activated.
                    You can now sign in and start shopping.
                  </p>

                  <div class="success-actions">
                    <v-btn
                        color="primary"
                        size="large"
                        class="action-btn"
                        @click="goToLogin"
                    >
                      <v-icon start icon="mdi-login"></v-icon>
                      Sign In Now
                    </v-btn>

                    <v-btn
                        variant="outlined"
                        size="large"
                        class="action-btn mt-3"
                        @click="goToHome"
                    >
                      <v-icon start icon="mdi-home"></v-icon>
                      Go to Homepage
                    </v-btn>
                  </div>
                </div>
              </div>

              <!-- Error State -->
              <div v-else-if="hasError" class="activate-error">
                <div class="error-content">
                  <v-icon
                      :icon="errorIcon"
                      size="64"
                      color="error"
                      class="error-icon mb-4"
                  ></v-icon>
                  <h2 class="error-title">{{ errorTitle }}</h2>
                  <p class="error-subtitle">{{ errorMessage }}</p>

                  <div class="error-actions">
                    <v-btn
                        color="primary"
                        size="large"
                        class="action-btn"
                        @click="retryActivation"
                        v-if="canRetry"
                    >
                      <v-icon start icon="mdi-refresh"></v-icon>
                      Try Again
                    </v-btn>

                    <!-- Show Resend Button if token expired (410) -->
                    <v-btn
                        color="warning"
                        size="large"
                        class="action-btn"
                        :class="{ 'mt-3': canRetry }"
                        @click="handleResendActivation"
                        v-if="isTokenExpired"
                    >
                      <v-icon start icon="mdi-email-refresh"></v-icon>
                      Resend Activation Email
                    </v-btn>

                    <!-- Show Register Button for other errors (404, etc.) -->
                    <v-btn
                        variant="outlined"
                        size="large"
                        class="action-btn"
                        :class="{ 'mt-3': canRetry || isTokenExpired }"
                        @click="goToRegister"
                        v-if="shouldShowRegister && !isTokenExpired"
                    >
                      <v-icon start icon="mdi-account-plus"></v-icon>
                      Register New Account
                    </v-btn>

                    <v-btn
                        variant="outlined"
                        size="large"
                        class="action-btn"
                        :class="{ 'mt-3': canRetry || shouldShowRegister || isTokenExpired }"
                        @click="goToHome"
                    >
                      <v-icon start icon="mdi-home"></v-icon>
                      Go to Homepage
                    </v-btn>
                  </div>
                </div>
              </div>

              <!-- Invalid Link State -->
              <div v-else class="activate-invalid">
                <div class="invalid-content">
                  <v-icon
                      icon="mdi-link-off"
                      size="64"
                      color="warning"
                      class="invalid-icon mb-4"
                  ></v-icon>
                  <h2 class="invalid-title">Invalid Activation Link</h2>
                  <p class="invalid-subtitle">
                    The activation link is missing required parameters.
                    Please check your email and click the activation link again.
                  </p>

                  <div class="invalid-actions">
                    <v-btn
                        color="primary"
                        size="large"
                        class="action-btn"
                        @click="goToRegister"
                    >
                      <v-icon start icon="mdi-account-plus"></v-icon>
                      Register Account
                    </v-btn>

                    <v-btn
                        variant="outlined"
                        size="large"
                        class="action-btn mt-3"
                        @click="goToHome"
                    >
                      <v-icon start icon="mdi-home"></v-icon>
                      Go to Homepage
                    </v-btn>
                  </div>
                </div>
              </div>
            </v-card>
          </div>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script setup>
import {computed, onMounted, ref, watch} from 'vue'
import {useTheme} from 'vuetify'
import {useAccountStore} from '@/stores/accounts'
import {useNavigation} from '@/composables/accounts/useNavigation'

const props = defineProps({
  email: {
    type: String,
    default: ''
  },
  token: {
    type: String,
    default: ''
  }
})

const theme = useTheme()
const accountStore = useAccountStore()

const {
  goToLogin,
  goToRegister,
  goToHome,
  goToResendActivation
} = useNavigation()

const activationAttempted = ref(false)

const isDarkTheme = computed(() => theme.global.current.value.dark)
const isLoading = computed(() => accountStore.isActivating)
const activationSuccess = computed(() => accountStore.activationSuccess)
const hasError = computed(() => accountStore.hasActivationError)
const errorMessage = computed(() => accountStore.activationErrorMessage)
const isTokenExpired = computed(() => accountStore.isTokenExpired)

const hasValidParams = computed(() => {
  return props.email && props.token
})

const errorIcon = computed(() => {
  const status = accountStore.activationError?.status
  switch (status) {
    case 410:
      return 'mdi-clock-alert'
    case 404:
      return 'mdi-account-question'
    case 400:
      return 'mdi-shield-alert'
    default:
      return 'mdi-alert-circle'
  }
})

const errorTitle = computed(() => {
  const status = accountStore.activationError?.status
  switch (status) {
    case 410:
      return 'Link Expired'
    case 404:
      return 'User Not Found'
    case 400:
      return 'Invalid Request'
    default:
      return 'Activation Failed'
  }
})

const canRetry = computed(() => {
  const status = accountStore.activationError?.status
  return status === 500 && hasValidParams.value
})

const shouldShowRegister = computed(() => {
  const status = accountStore.activationError?.status
  return status === 404
})

const activateAccount = async () => {
  if (!hasValidParams.value || activationAttempted.value) {
    return
  }

  activationAttempted.value = true

  const result = await accountStore.activate({
    email: props.email,
    token: props.token
  })

  if (result.success) {
    console.log('Account activated successfully:', result.data)
  } else {
    console.error('Account activation failed:', result.error)
  }
}

const retryActivation = async () => {
  activationAttempted.value = false
  accountStore.clearActivationState()
  await activateAccount()
}

const handleResendActivation = () => {
  goToResendActivation(props.email)
}

watch([() => props.email, () => props.token], ([newEmail, newToken]) => {
  if (newEmail && newToken && !activationAttempted.value) {
    accountStore.clearActivationState()
    activateAccount()
  }
})

onMounted(() => {
  document.title = 'StyleShop - Activate Account'

  accountStore.clearActivationState()

  if (hasValidParams.value && !activationAttempted.value) {
    activateAccount()
  }
})
</script>

<style scoped>
.activate-page {
  width: 100%;
}

.activate-container {
  min-height: calc(100vh - 64px);
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  position: relative;
}

.min-height-screen {
  min-height: calc(100vh - 104px);
}

.activate-card-wrapper {
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

.activate-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 24px;
  overflow: hidden;
  transition: all 0.3s ease;
  animation: slideInUp 0.6s ease-out;
  min-height: 400px;
}

.activate-card.dark-theme {
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

.activate-loading,
.activate-success,
.activate-error,
.activate-invalid {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  padding: 40px 24px;
}

.loading-content,
.success-content,
.error-content,
.invalid-content {
  text-align: center;
  max-width: 400px;
}

.loading-title,
.success-title,
.error-title,
.invalid-title {
  font-size: 1.75rem;
  font-weight: 600;
  margin: 0 0 16px;
  color: inherit;
}

.loading-subtitle,
.success-subtitle,
.error-subtitle,
.invalid-subtitle {
  font-size: 1rem;
  opacity: 0.8;
  margin: 0 0 32px;
  line-height: 1.5;
}

.success-icon {
  animation: checkmark 0.6s ease-in-out;
}

.error-icon,
.invalid-icon {
  animation: shake 0.6s ease-in-out;
}

@keyframes checkmark {
  0% {
    transform: scale(0);
    opacity: 0;
  }
  50% {
    transform: scale(1.2);
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

@keyframes shake {
  0%, 100% {
    transform: translateX(0);
  }
  25% {
    transform: translateX(-5px);
  }
  75% {
    transform: translateX(5px);
  }
}

.success-actions,
.error-actions,
.invalid-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
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
  .activate-container {
    padding: 10px;
  }

  .activate-loading,
  .activate-success,
  .activate-error,
  .activate-invalid {
    padding: 24px 16px;
    min-height: 350px;
  }

  .loading-title,
  .success-title,
  .error-title,
  .invalid-title {
    font-size: 1.5rem;
  }

  .loading-subtitle,
  .success-subtitle,
  .error-subtitle,
  .invalid-subtitle {
    font-size: 0.9rem;
  }
}

:deep(.v-theme--dark .activate-container) {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
}
</style>
