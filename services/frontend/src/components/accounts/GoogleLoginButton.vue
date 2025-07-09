<template>
  <v-btn
      variant="outlined"
      block
      size="large"
      class="social-btn google-btn mb-2"
      :disabled="isLoading || isSocialAuthLoading"
      :loading="isSocialAuthLoading && socialAuthType === 'google'"
      @click="$emit('login')"
  >
    <v-icon start icon="mdi-google" />
    {{ buttonText }}
  </v-btn>
</template>

<script setup>
import {computed} from 'vue';

const props = defineProps({
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

defineEmits(['login']);

const buttonText = computed(() => {
  return (props.isSocialAuthLoading && props.socialAuthType === 'google')
    ? 'Connecting...'
    : 'Continue with Google';
});
</script>

<style scoped>
.google-btn {
  border-color: #4285f4;
  color: #4285f4;
}

.google-btn:hover {
  background-color: rgba(66, 133, 244, 0.04);
}
</style>
