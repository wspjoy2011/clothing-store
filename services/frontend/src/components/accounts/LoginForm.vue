<template>
  <v-form
      ref="formRef"
      v-model="isFormValid"
      @submit.prevent="handleSubmit"
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
          :error="emailTouched && emailHasError"
          :error-messages="emailTouched && emailHasError ? emailDisplayErrorMessage : ''"
          @focus="handleEmailFocus"
          @input="handleClearLoginError"
          autocomplete="email"
      />
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
          :error="passwordTouched && passwordHasError"
          :error-messages="passwordTouched && passwordHasError ? passwordDisplayErrorMessage : ''"
          @focus="handlePasswordFocus"
          @input="handleClearLoginError"
          autocomplete="current-password"
      />
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
        <v-icon start icon="mdi-login"/>
        {{ isLoading ? 'Signing In...' : 'Sign In' }}
      </v-btn>
    </div>

    <!-- Action buttons for errors -->
    <login-actions
        v-if="showActionButtons"
        :needs-activation="needsActivation"
        :needs-registration="needsRegistration"
        :is-loading="isLoading"
        :is-social-auth-loading="isSocialAuthLoading"
        :email="email"
        @activate="$emit('activate', email)"
        @register="$emit('register')"
    />
  </v-form>
</template>

<script setup>
import {useLoginForm} from '@/composables/accounts/useLoginForm';
import {watch} from 'vue';
import LoginActions from './LoginActions.vue';

const props = defineProps({
  isLoading: {
    type: Boolean,
    default: false
  },
  isSocialAuthLoading: {
    type: Boolean,
    default: false
  },
  needsActivation: {
    type: Boolean,
    default: false
  },
  needsRegistration: {
    type: Boolean,
    default: false
  },
  showActionButtons: {
    type: Boolean,
    default: false
  },
  loginError: {
    type: String,
    default: ''
  },
  showLoginError: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['submit', 'activate', 'register', 'clear-login-error']);

const {
  formRef,
  isFormValid,
  email,
  password,
  showPassword,
  emailTouched,
  passwordTouched,
  emailRules,
  passwordRules,
  emailHasError,
  passwordHasError,
  emailDisplayErrorMessage,
  passwordDisplayErrorMessage,
  isFormReady,
  setLoginError,
  clearLoginError
} = useLoginForm();

watch(() => props.loginError, (newError) => {
  if (newError && props.showLoginError) {
    setLoginError(newError);
  }
});

watch(() => props.showLoginError, (show) => {
  if (!show) {
    clearLoginError();
  }
});

const handleEmailFocus = () => {
  emailTouched.value = true;
};

const handlePasswordFocus = () => {
  passwordTouched.value = true;
};

const handleSubmit = () => {
  if (!isFormReady.value || props.isLoading) return;

  emit('submit', {
    email: email.value,
    password: password.value
  });
};

const handleClearLoginError = () => {
  clearLoginError();
  emit('clear-login-error');
};
</script>

<style scoped>
.form-field-wrapper {
  margin-bottom: 16px;
}

.animated-field {
  transition: all 0.3s ease;
}

.login-btn {
  font-weight: 600;
  text-transform: none;
}
</style>
