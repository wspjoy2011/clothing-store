<template>
  <div>
    <!-- Success Messages -->
    <v-snackbar
        v-model="localShowSuccessMessage"
        color="success"
        timeout="5000"
        location="top"
    >
      <v-icon start icon="mdi-check-circle" />
      {{ successMessage }}
      <template v-slot:actions>
        <v-btn variant="text" @click="hideSuccess">
          Close
        </v-btn>
      </template>
    </v-snackbar>

    <!-- Error Messages -->
    <v-snackbar
        v-model="localShowErrorMessage"
        color="error"
        timeout="8000"
        location="top"
    >
      <v-icon start icon="mdi-alert-circle" />
      {{ errorMessage }}
      <template v-slot:actions>
        <v-btn variant="text" @click="hideError">
          Close
        </v-btn>
      </template>
    </v-snackbar>

    <!-- Warning Messages -->
    <v-snackbar
        v-model="localShowWarningMessage"
        color="warning"
        timeout="6000"
        location="top"
    >
      <v-icon start icon="mdi-alert" />
      {{ warningMessage }}
      <template v-slot:actions>
        <v-btn variant="text" @click="hideWarning">
          Close
        </v-btn>
      </template>
    </v-snackbar>

    <!-- Social Auth Success -->
    <v-snackbar
        v-model="localShowSocialSuccessMessage"
        color="success"
        timeout="6000"
        location="top"
    >
      <v-icon start :icon="socialAuthType === 'google' ? 'mdi-google' : 'mdi-facebook'" />
      {{ socialSuccessMessage }}
      <template v-slot:actions>
        <v-btn variant="text" @click="hideSocialSuccess">
          Close
        </v-btn>
      </template>
    </v-snackbar>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';

const props = defineProps({
  showSuccessMessage: {
    type: Boolean,
    default: false
  },
  showErrorMessage: {
    type: Boolean,
    default: false
  },
  showWarningMessage: {
    type: Boolean,
    default: false
  },
  showSocialSuccessMessage: {
    type: Boolean,
    default: false
  },
  successMessage: {
    type: String,
    default: ''
  },
  errorMessage: {
    type: String,
    default: ''
  },
  warningMessage: {
    type: String,
    default: ''
  },
  socialSuccessMessage: {
    type: String,
    default: ''
  },
  socialAuthType: {
    type: String,
    default: ''
  }
});

const emit = defineEmits(['hide-success', 'hide-error', 'hide-warning', 'hide-social-success']);

const localShowSuccessMessage = ref(props.showSuccessMessage);
const localShowErrorMessage = ref(props.showErrorMessage);
const localShowWarningMessage = ref(props.showWarningMessage);
const localShowSocialSuccessMessage = ref(props.showSocialSuccessMessage);

watch(() => props.showSuccessMessage, (newValue) => {
  localShowSuccessMessage.value = newValue;
});

watch(() => props.showErrorMessage, (newValue) => {
  localShowErrorMessage.value = newValue;
});

watch(() => props.showWarningMessage, (newValue) => {
  localShowWarningMessage.value = newValue;
});

watch(() => props.showSocialSuccessMessage, (newValue) => {
  localShowSocialSuccessMessage.value = newValue;
});

const hideSuccess = () => {
  localShowSuccessMessage.value = false;
  emit('hide-success');
};

const hideError = () => {
  localShowErrorMessage.value = false;
  emit('hide-error');
};

const hideWarning = () => {
  localShowWarningMessage.value = false;
  emit('hide-warning');
};

const hideSocialSuccess = () => {
  localShowSocialSuccessMessage.value = false;
  emit('hide-social-success');
};

watch(localShowSuccessMessage, (newValue) => {
  if (!newValue && props.showSuccessMessage) {
    emit('hide-success');
  }
});

watch(localShowErrorMessage, (newValue) => {
  if (!newValue && props.showErrorMessage) {
    emit('hide-error');
  }
});

watch(localShowWarningMessage, (newValue) => {
  if (!newValue && props.showWarningMessage) {
    emit('hide-warning');
  }
});

watch(localShowSocialSuccessMessage, (newValue) => {
  if (!newValue && props.showSocialSuccessMessage) {
    emit('hide-social-success');
  }
});
</script>
