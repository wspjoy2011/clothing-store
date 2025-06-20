<template>
  <div class="resend-activation-page">
    <v-container class="resend-activation-container">
      <v-row justify="center" align="center" class="min-height-screen">
        <v-col cols="12" sm="8" md="6" lg="4" xl="3">
          <div class="resend-card-wrapper">
            <div class="floating-shapes">
              <div class="shape shape-1"></div>
              <div class="shape shape-2"></div>
              <div class="shape shape-3"></div>
              <div class="shape shape-4"></div>
            </div>

            <v-card
                elevation="12"
                class="resend-card"
                :class="{ 'dark-theme': isDarkTheme }"
            >
              <v-card-title class="text-center pa-6 resend-card-title" :class="{ 'dark-theme': isDarkTheme }">
                <v-icon size="48" color="primary" class="mb-4">mdi-email-refresh</v-icon>
                <h1 class="text-h4 font-weight-bold">Resend Activation Email</h1>
                <p class="text-subtitle-1 text-medium-emphasis mt-2">
                  Enter your email address to receive a new activation link
                </p>
              </v-card-title>

              <v-card-text class="pa-6">
                <!-- Success Message -->
                <v-alert
                    v-if="resendSuccess"
                    type="success"
                    variant="tonal"
                    class="mb-6"
                    icon="mdi-check-circle"
                >
                  <div class="text-subtitle-1 font-weight-medium">
                    Activation email sent successfully!
                  </div>
                  <div class="text-body-2 mt-1">
                    Please check your inbox and follow the activation link.
                  </div>
                </v-alert>

                <!-- Error Message -->
                <v-alert
                    v-if="hasResendError"
                    type="error"
                    variant="tonal"
                    class="mb-6"
                    icon="mdi-alert-circle"
                >
                  <div class="text-subtitle-1 font-weight-medium">
                    {{ resendErrorMessage }}
                  </div>
                </v-alert>

                <!-- Form -->
                <v-form
                    v-if="!resendSuccess"
                    ref="resendForm"
                    v-model="formValid"
                    @submit.prevent="handleResendActivation"
                >
                  <v-text-field
                      v-model="email"
                      label="Email Address"
                      type="email"
                      variant="outlined"
                      density="comfortable"
                      prepend-inner-icon="mdi-email"
                      :rules="emailRules"
                      :disabled="isResending"
                      class="mb-4"
                      required
                  />

                  <v-btn
                      type="submit"
                      color="primary"
                      size="large"
                      block
                      :loading="isResending"
                      :disabled="!formValid || isResending"
                      class="mb-4 action-btn"
                  >
                    <v-icon start>mdi-email-send</v-icon>
                    Send New Activation Email
                  </v-btn>
                </v-form>

                <!-- Success Actions -->
                <div v-if="resendSuccess" class="text-center">
                  <v-btn
                      color="primary"
                      variant="outlined"
                      size="large"
                      class="action-btn"
                      @click="resetForm"
                  >
                    <v-icon start>mdi-refresh</v-icon>
                    Send Another Email
                  </v-btn>
                </div>

                <!-- Additional Links -->
                <div v-if="!resendSuccess" class="text-center mt-6">
                  <v-btn
                      color="primary"
                      variant="text"
                      class="action-btn"
                      @click="goToRegister"
                  >
                    <v-icon start>mdi-account-plus</v-icon>
                    Create New Account
                  </v-btn>
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
                        Activation links expire after 7 days. Request a new one here.
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
import {ref, computed, onMounted, onUnmounted} from 'vue'
import {useRouter} from 'vue-router'
import {useTheme} from 'vuetify'
import {useAccountStore} from '@/stores/accounts'
import {useNotifications} from '@/composables/accounts/useNotifications'

const props = defineProps({
  email: {
    type: String,
    default: ''
  }
})

const router = useRouter()
const theme = useTheme()
const accountStore = useAccountStore()
const {showSuccess, showError} = useNotifications()

const email = ref(props.email)
const formValid = ref(false)
const resendForm = ref(null)

const isDarkTheme = computed(() => theme.global.current.value.dark)
const isResending = computed(() => accountStore.isResending)
const hasResendError = computed(() => accountStore.hasResendError)
const resendErrorMessage = computed(() => accountStore.resendErrorMessage)
const resendSuccess = computed(() => accountStore.resendSuccess)

const emailRules = [
  v => !!v || 'Email is required',
  v => /.+@.+\..+/.test(v) || 'Please enter a valid email address',
]

const handleResendActivation = async () => {
  if (!formValid.value) return

  try {
    const result = await accountStore.resendActivation({email: email.value})

    if (result.success) {
      showSuccess(result.message || 'Activation email sent successfully!')
    } else {
      showError(result.message || 'Failed to send activation email')
    }
  } catch (error) {
    console.error('Resend activation error:', error)
    showError('An unexpected error occurred')
  }
}

const resetForm = () => {
  accountStore.clearResendState()
  email.value = ''
  if (resendForm.value) {
    resendForm.value.resetValidation()
  }
}

const goToRegister = () => {
  router.push({name: 'register'})
}

onMounted(() => {
  document.title = 'StyleShop - Resend Activation'
  accountStore.clearResendState()
})

onUnmounted(() => {
  accountStore.clearResendState()
})
</script>

<style scoped>
.resend-activation-page {
  width: 100%;
}

.resend-activation-container {
  min-height: calc(100vh - 64px);
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  position: relative;
}

.min-height-screen {
  min-height: calc(100vh - 104px);
}

.resend-card-wrapper {
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

.resend-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 24px;
  overflow: hidden;
  transition: all 0.3s ease;
  animation: slideInUp 0.6s ease-out;
}

.resend-card.dark-theme {
  background: rgba(30, 30, 30, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.resend-card-title {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
}

.resend-card-title.dark-theme {
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
  .resend-activation-container {
    padding: 10px;
  }

  .resend-card-title {
    padding: 24px 16px !important;
  }

  .resend-card .v-card-text {
    padding: 24px 16px !important;
  }
}

:deep(.v-theme--dark .resend-activation-container) {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
}
</style>
