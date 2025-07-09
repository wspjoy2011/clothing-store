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
              <activation-status-card
                  :is-loading="isLoading"
                  :activation-success="activationSuccess"
                  :has-error="hasError"
                  :error-message="errorMessage"
                  :error-details="getErrorDetails"
              />

              <activation-actions
                  :activation-success="activationSuccess"
                  :has-error="hasError"
                  :error-details="getErrorDetails"
                  @go-login="goToLogin"
                  @go-home="goToHome"
                  @go-register="goToRegister"
                  @retry="retryActivation"
                  @resend="handleResendActivation"
              />
            </v-card>
          </div>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script setup>
import {useActivationPage} from '@/composables/accounts/useActivationPage';
import ActivationStatusCard from '@/components/accounts/ActivationStatusCard.vue';
import ActivationActions from '@/components/accounts/ActivationActions.vue';

const props = defineProps({
  email: {
    type: String,
    default: ''
  },
  token: {
    type: String,
    default: ''
  }
});

const {
  isDarkTheme,
  isLoading,
  activationSuccess,
  hasError,
  errorMessage,
  getErrorDetails,
  retryActivation,
  handleResendActivation,
  goToLogin,
  goToRegister,
  goToHome
} = useActivationPage(props);
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

@media (max-width: 600px) {
  .activate-container {
    padding: 10px;
  }

  .activate-card {
    margin: 1rem;
    border-radius: 16px;
  }
}

:deep(.v-theme--dark .activate-container) {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
}
</style>
