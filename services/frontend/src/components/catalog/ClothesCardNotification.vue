<template>
  <transition name="fade">
    <div
      v-if="active"
      class="floating-notification"
      :class="type"
      :style="customStyles"
    >
      <v-icon class="notif-icon" size="22">
        {{
          type === 'success' ? 'mdi-check-circle'
          : type === 'error' ? 'mdi-alert-circle'
          : 'mdi-alert'
        }}
      </v-icon>
      <span class="notif-text">{{ text }}</span>
      <div class="notif-progress-bar">
        <div
          class="notif-progress"
          :style="{ width: progress + '%', background: progressColor }"
        ></div>
      </div>
      <v-btn icon class="notif-close-btn" size="x-small" @click="close">
        <v-icon size="18">mdi-close</v-icon>
      </v-btn>
    </div>
  </transition>
</template>

<script setup>
import { computed } from 'vue'
const props = defineProps({
  active: Boolean,
  type: String,
  text: String,
  progress: Number,
  close: Function,
  color: String
})

const progressColor = computed(() => {
  if (props.color && props.type === 'success') return props.color
  if (props.type === 'error') return '#d32f2f'
  if (props.type === 'warning') return '#f9a825'
  return '#43a047'
})

const customStyles = computed(() => {
  if (props.color && props.type === 'success') {
    return {
      borderLeft: `5px solid ${props.color}`,
      color: props.color
    }
  }
  return {}
})
</script>

<style scoped>
.floating-notification {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  margin: 0 auto;
  z-index: 10;
  min-width: 0;
  width: 100%;
  max-width: 100%;
  height: 48px;
  padding: 12px 16px 12px 44px;
  border-radius: 12px 12px 0 0;
  box-shadow: 0 4px 32px rgba(80,80,80,0.13);
  font-size: 1rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  background: #fff;
  color: #2e7d32;
  opacity: 0.97;
  animation: fadein-notif 0.22s;
  pointer-events: auto;
}
.floating-notification.success { border-left: 5px solid #43a047; }
.floating-notification.error { border-left: 5px solid #d32f2f; color: #d32f2f; }
.floating-notification.warning { border-left: 5px solid #f9a825; color: #a68104; }
.floating-notification .notif-icon { position: absolute; left: 14px; top: 14px; }
.floating-notification .notif-text { flex: 1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.floating-notification .notif-close-btn { margin-left: 10px; }
.floating-notification .notif-progress-bar {
  margin: 0;
  padding: 0;
  width: 100%;
  height: 3px;
  border-radius: 0 0 2px 2px;
  background: #e0e0e0;
  position: absolute;
  left: 0;
  bottom: 0;
  overflow: hidden;
}
.floating-notification .notif-progress {
  height: 100%;
  transition: width 30ms linear;
}
@keyframes fadein-notif {
  from { opacity: 0; transform: translateY(-70%);}
  to { opacity: 0.97; transform: translateY(0%);}
}
</style>
