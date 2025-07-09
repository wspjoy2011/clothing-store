<template>
  <div class="logout-header">
    <v-icon
        :icon="statusIcon"
        :color="statusColor"
        size="64"
        class="logout-icon mb-4"
    ></v-icon>
    <h1 class="logout-title">{{ statusTitle }}</h1>
    <p class="logout-subtitle">{{ statusSubtitle }}</p>
  </div>
</template>

<script setup>
import {computed} from 'vue';

const props = defineProps({
  isLoading: {
    type: Boolean,
    default: false
  },
  logoutSuccess: {
    type: Boolean,
    default: false
  },
  logoutError: {
    type: String,
    default: null
  },
  isDarkTheme: {
    type: Boolean,
    default: false
  }
});

const statusIcon = computed(() => {
  if (props.isLoading) return 'mdi-loading';
  if (props.logoutSuccess) return 'mdi-check-circle';
  if (props.logoutError) return 'mdi-alert-circle';
  return 'mdi-logout';
});

const statusColor = computed(() => {
  if (props.isLoading) return 'primary';
  if (props.logoutSuccess) return 'success';
  if (props.logoutError) return 'error';
  return 'primary';
});

const statusTitle = computed(() => {
  if (props.isLoading) return 'Signing Out';
  if (props.logoutSuccess) return 'You have been successfully logged out';
  if (props.logoutError) return 'Logout Error';
  return 'Logout';
});

const statusSubtitle = computed(() => {
  if (props.isLoading) return 'Please wait while we sign you out...';
  if (props.logoutSuccess) return 'Your session has been safely terminated';
  if (props.logoutError) return 'There was an issue, but you are logged out locally';
  return 'Logout process';
});
</script>

<style scoped>
.logout-header {
  text-align: center;
  padding: 2rem 2rem 1rem;
}

.logout-title {
  font-size: 1.75rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: rgba(0, 0, 0, 0.87);
}

.logout-subtitle {
  color: rgba(0, 0, 0, 0.6);
  font-size: 1rem;
  margin: 0;
}

@media (max-width: 600px) {
  .logout-header {
    padding: 1.5rem 1.5rem 1rem;
  }
}
</style>
