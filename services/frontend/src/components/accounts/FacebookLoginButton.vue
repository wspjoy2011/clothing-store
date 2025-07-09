<template>
  <HFaceBookLogin
      :app-id="appId"
      scope="email,public_profile"
      fields="id,name,email,first_name,last_name,birthday"
      @onSuccess="$emit('success', $event)"
      @onFailure="$emit('error', $event)"
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
      <v-icon start icon="mdi-facebook" />
      {{ buttonText }}
    </v-btn>
  </HFaceBookLogin>
</template>

<script setup>
import {computed} from 'vue';
import {HFaceBookLogin} from '@healerlab/vue3-facebook-login';

const props = defineProps({
  appId: {
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

defineEmits(['success', 'error']);

const buttonText = computed(() => {
  return (props.isSocialAuthLoading && props.socialAuthType === 'facebook')
    ? 'Connecting...'
    : 'Continue with Facebook';
});
</script>

<style scoped>
.facebook-btn {
  border-color: #1877f2;
  color: #1877f2;
}

.facebook-btn:hover {
  background-color: rgba(24, 119, 242, 0.04);
}

.facebook-login-wrapper {
  width: 100%;
}
</style>
