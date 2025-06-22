<template>
  <div class="content-loader-overlay" :class="{ 'dark-theme': isDarkTheme }">
    <div class="loader-container">
      <!-- Main Loader -->
      <div class="main-loader">
        <div class="spinner-ring">
          <div class="spinner-inner"></div>
        </div>

        <!-- Animated Dots -->
        <div class="loading-dots">
          <div class="dot dot-1"></div>
          <div class="dot dot-2"></div>
          <div class="dot dot-3"></div>
        </div>

        <!-- Loading Text -->
        <div class="loading-text">
          <h3 class="loading-title" :class="{ 'dark-theme': isDarkTheme }">{{ loadingTitle }}</h3>
          <p class="loading-subtitle" :class="{ 'dark-theme': isDarkTheme }">{{ loadingSubtitle }}</p>
        </div>
      </div>

      <!-- Floating Elements -->
      <div class="floating-elements">
        <div class="floating-element element-1" :class="{ 'dark-theme': isDarkTheme }"></div>
        <div class="floating-element element-2" :class="{ 'dark-theme': isDarkTheme }"></div>
        <div class="floating-element element-3" :class="{ 'dark-theme': isDarkTheme }"></div>
        <div class="floating-element element-4" :class="{ 'dark-theme': isDarkTheme }"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import {computed} from 'vue'
import {useTheme} from 'vuetify'

const props = defineProps({
  color: {
    type: String,
    default: 'primary'
  },
  size: {
    type: Number,
    default: 120
  },
  title: {
    type: String,
    default: 'Loading'
  },
  subtitle: {
    type: String,
    default: 'Please wait while we load your content...'
  },
  overlay: {
    type: Boolean,
    default: true
  }
})

const theme = useTheme()

const isDarkTheme = computed(() => theme.global.current.value.dark)

const loadingTitle = computed(() => props.title)
const loadingSubtitle = computed(() => props.subtitle)

const loaderSize = computed(() => `${props.size}px`)

const primaryColor = computed(() => {
  const colors = theme.current.value.colors
  return colors[props.color] || colors.primary || '#1976d2'
})

const primaryColorDark = computed(() => {
  if (isDarkTheme.value) {
    const colors = theme.current.value.colors
    return colors[props.color] || colors.primary || '#90CAF9'
  }
  return primaryColor.value
})
</script>

<style scoped>
.content-loader-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(8px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
  animation: fadeIn 0.3s ease-out;
  transition: background-color 0.3s ease;
}

.content-loader-overlay.dark-theme {
  background: rgba(18, 18, 18, 0.95);
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.loader-container {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  perspective: 1000px;
}

.main-loader {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  animation: slideUp 0.6s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.spinner-ring {
  width: v-bind(loaderSize);
  height: v-bind(loaderSize);
  position: relative;
  margin-bottom: 2rem;
}

.spinner-ring::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border: 4px solid rgba(0, 0, 0, 0.1);
  border-radius: 50%;
  animation: pulse 2s ease-in-out infinite;
  transition: border-color 0.3s ease;
}

.dark-theme .spinner-ring::before {
  border-color: rgba(255, 255, 255, 0.1);
}

.spinner-inner {
  width: 100%;
  height: 100%;
  border: 4px solid transparent;
  border-top: 4px solid v-bind(primaryColorDark);
  border-right: 4px solid v-bind(primaryColorDark);
  border-radius: 50%;
  animation: spin 1.2s cubic-bezier(0.68, -0.55, 0.265, 1.55) infinite;
  position: relative;
  transition: border-color 0.3s ease;
}

.spinner-inner::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 60%;
  height: 60%;
  border: 3px solid transparent;
  border-bottom: 3px solid v-bind(primaryColorDark);
  border-left: 3px solid v-bind(primaryColorDark);
  border-radius: 50%;
  transform: translate(-50%, -50%);
  animation: spinReverse 1.5s linear infinite;
  opacity: 0.7;
  transition: border-color 0.3s ease;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

@keyframes spinReverse {
  from {
    transform: translate(-50%, -50%) rotate(360deg);
  }
  to {
    transform: translate(-50%, -50%) rotate(0deg);
  }
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    opacity: 0.3;
  }
  50% {
    transform: scale(1.1);
    opacity: 0.1;
  }
}

.loading-dots {
  display: flex;
  gap: 8px;
  margin-bottom: 1.5rem;
}

.dot {
  width: 12px;
  height: 12px;
  background: v-bind(primaryColorDark);
  border-radius: 50%;
  animation: bounce 1.4s ease-in-out infinite both;
  transition: background-color 0.3s ease;
}

.dot-1 {
  animation-delay: -0.32s;
}

.dot-2 {
  animation-delay: -0.16s;
}

.dot-3 {
  animation-delay: 0s;
}

@keyframes bounce {
  0%, 80%, 100% {
    transform: scale(0.8);
    opacity: 0.5;
  }
  40% {
    transform: scale(1.2);
    opacity: 1;
  }
}

.loading-text {
  text-align: center;
  max-width: 300px;
}

.loading-title {
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0 0 0.5rem;
  color: v-bind(primaryColorDark);
  animation: textGlow 2s ease-in-out infinite alternate;
  transition: color 0.3s ease;
}

.loading-title.dark-theme {
  text-shadow: 0 0 10px rgba(144, 202, 249, 0.4);
}

.loading-subtitle {
  font-size: 1rem;
  margin: 0;
  opacity: 0.7;
  line-height: 1.4;
  animation: fadeInOut 3s ease-in-out infinite;
  color: inherit;
  transition: color 0.3s ease;
}

.loading-subtitle.dark-theme {
  color: rgba(255, 255, 255, 0.8);
}

@keyframes textGlow {
  from {
    text-shadow: 0 0 5px rgba(25, 118, 210, 0.3);
  }
  to {
    text-shadow: 0 0 15px rgba(25, 118, 210, 0.6);
  }
}

@keyframes fadeInOut {
  0%, 100% {
    opacity: 0.7;
  }
  50% {
    opacity: 1;
  }
}

.floating-elements {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.floating-element {
  position: absolute;
  background: linear-gradient(45deg, v-bind(primaryColorDark), rgba(25, 118, 210, 0.3));
  border-radius: 50%;
  opacity: 0.6;
  animation: float 8s ease-in-out infinite;
  transition: background 0.3s ease;
}

.floating-element.dark-theme {
  background: linear-gradient(45deg, v-bind(primaryColorDark), rgba(144, 202, 249, 0.2));
  opacity: 0.4;
}

.element-1 {
  width: 60px;
  height: 60px;
  top: 10%;
  left: 10%;
  animation-delay: 0s;
}

.element-2 {
  width: 40px;
  height: 40px;
  top: 20%;
  right: 15%;
  animation-delay: 1s;
}

.element-3 {
  width: 80px;
  height: 80px;
  bottom: 15%;
  left: 20%;
  animation-delay: 2s;
}

.element-4 {
  width: 50px;
  height: 50px;
  bottom: 25%;
  right: 10%;
  animation-delay: 3s;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px) translateX(0px) rotate(0deg);
    opacity: 0.6;
  }
  25% {
    transform: translateY(-20px) translateX(10px) rotate(90deg);
    opacity: 0.3;
  }
  50% {
    transform: translateY(0px) translateX(-10px) rotate(180deg);
    opacity: 0.8;
  }
  75% {
    transform: translateY(20px) translateX(5px) rotate(270deg);
    opacity: 0.4;
  }
}

@media (max-width: 768px) {
  .spinner-ring {
    width: 80px;
    height: 80px;
  }

  .loading-title {
    font-size: 1.25rem;
  }

  .loading-subtitle {
    font-size: 0.9rem;
  }

  .floating-element {
    display: none;
  }
}

@media (max-width: 480px) {
  .spinner-ring {
    width: 60px;
    height: 60px;
  }

  .loading-title {
    font-size: 1.1rem;
  }

  .loading-subtitle {
    font-size: 0.8rem;
  }

  .dot {
    width: 8px;
    height: 8px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .spinner-inner,
  .spinner-inner::after,
  .dot,
  .floating-element {
    animation-duration: 3s;
  }

  .loading-title,
  .loading-subtitle {
    animation: none;
  }
}
</style>
