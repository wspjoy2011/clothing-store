<template>
  <div class="social-login-section mb-6">
    <google-login-button
        :is-loading="isLoading"
        :is-social-auth-loading="isSocialAuthLoading"
        :social-auth-type="socialAuthType"
        @login="$emit('google-login')"
    />

    <facebook-login-button
        :app-id="facebookAppId"
        :is-loading="isLoading"
        :is-social-auth-loading="isSocialAuthLoading"
        :social-auth-type="socialAuthType"
        @success="$emit('facebook-success', $event)"
        @error="$emit('facebook-error', $event)"
    />
  </div>
</template>

<script setup>
import GoogleLoginButton from './GoogleLoginButton.vue';
import FacebookLoginButton from './FacebookLoginButton.vue';

defineProps({
  facebookAppId: {
    type: String,
    required: true
  },
  isLoading: {
    type: Boolean,
    default: false
  },
  isSocialAuthLoading: {
    type: Boolean,
    default: false
  },
  socialAuthType: {
    type: String,
    default: ''
  }
});

defineEmits(['google-login', 'facebook-success', 'facebook-error']);
</script>

<style scoped>
.social-login-section {
  margin-bottom: 24px;
}
</style>
