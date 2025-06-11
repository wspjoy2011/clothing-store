<template>
  <v-dialog v-model="dialog" max-width="800" scrollable persistent>
    <v-card class="privacy-modal">
      <v-card-title class="privacy-header">
        <v-icon start icon="mdi-shield-account-outline" size="28"></v-icon>
        <span class="privacy-title">Privacy Policy</span>
        <v-spacer></v-spacer>
        <div class="reading-progress">
          <v-chip
              :color="hasScrolledToBottom ? 'white' : 'orange'"
              size="small"
              variant="flat"
              :class="{ 'text-green-darken-3': hasScrolledToBottom }"
          >
            {{ hasScrolledToBottom ? 'Read' : 'Reading...' }}
          </v-chip>
        </div>
        <v-btn icon variant="text" @click="closeModal">
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-card-title>

      <v-divider></v-divider>

      <v-card-text
          ref="scrollElement"
          class="privacy-content"
          @scroll="onScroll"
      >
        <div class="privacy-text">
          <div class="effective-date">
            <v-chip color="success" size="small" variant="tonal">
              Last Updated: {{ lastUpdated }}
            </v-chip>
          </div>

          <section class="privacy-section">
            <h3 class="section-title">1. Information We Collect</h3>
            <p class="section-text">
              At StyleShop, we collect information that you provide directly to us, such as when you
              create an account, make a purchase, or contact our customer service. This includes your
              name, email address, shipping address, payment information, and communication preferences.
              We also automatically collect certain information about your device and usage patterns
              when you visit our website, including IP address, browser type, pages visited, and time
              spent on our platform to improve your shopping experience.
            </p>
          </section>

          <section class="privacy-section">
            <h3 class="section-title">2. How We Use Your Information</h3>
            <p class="section-text">
              We use the information we collect to provide, maintain, and improve our services,
              including processing transactions, communicating with you about your orders, and
              personalizing your shopping experience. Your information helps us recommend products
              that might interest you, send promotional communications (with your consent), prevent
              fraud, and comply with legal obligations. We may also use aggregated, non-personal
              information for analytics and business intelligence purposes.
            </p>
          </section>

          <section class="privacy-section">
            <h3 class="section-title">3. Information Sharing and Disclosure</h3>
            <p class="section-text">
              StyleShop does not sell, rent, or trade your personal information to third parties for
              their marketing purposes. We may share your information with trusted service providers
              who assist us in operating our website, conducting business, or servicing you, provided
              they agree to keep this information confidential. We may also disclose your information
              when required by law, to protect our rights, or in connection with a business transfer
              such as a merger or acquisition.
            </p>
          </section>

          <section class="privacy-section">
            <h3 class="section-title">4. Data Security and Your Rights</h3>
            <p class="section-text">
              We implement appropriate technical and organizational measures to protect your personal
              information against unauthorized access, alteration, disclosure, or destruction. However,
              no method of transmission over the internet is 100% secure. You have the right to access,
              update, or delete your personal information, and you may opt out of marketing communications
              at any time. If you have questions about our privacy practices or wish to exercise your
              rights, please contact us through the information provided on our website.
            </p>
          </section>

          <section class="privacy-section">
            <h3 class="section-title">5. Cookies and Tracking Technologies</h3>
            <p class="section-text">
              We use cookies and similar tracking technologies to enhance your browsing experience,
              analyze site traffic, and understand where our visitors are coming from. You can control
              cookie settings through your browser preferences, though disabling certain cookies may
              limit site functionality. We also use analytics tools to help us understand how users
              interact with our website and to improve our services.
            </p>
          </section>

          <section class="privacy-section">
            <h3 class="section-title">6. Children's Privacy</h3>
            <p class="section-text">
              StyleShop is not intended for children under the age of 13, and we do not knowingly
              collect personal information from children under 13. If we become aware that we have
              collected personal information from a child under 13, we will take steps to delete
              such information. Parents who believe their child has provided personal information
              to us should contact us immediately.
            </p>
          </section>
        </div>
      </v-card-text>

      <v-divider></v-divider>

      <v-card-actions class="privacy-actions">
        <div class="time-indicator">
          <v-chip
              size="small"
              variant="text"
              :color="legalStore.canAcknowledgePrivacy ? 'success' : 'grey'"
          >
            <v-icon start size="small">mdi-clock-outline</v-icon>
            {{ Math.floor(legalStore.privacyTimeSpent / 1000) }}s / {{
              Math.floor(legalStore.privacyMinReadTime / 1000)
            }}s
          </v-chip>
        </div>
        <v-spacer></v-spacer>
        <v-btn color="grey" variant="text" @click="closeModal">
          Close
        </v-btn>
        <v-btn
            color="success"
            variant="flat"
            :disabled="!legalStore.canAcknowledgePrivacy"
            @click="acknowledgePolicy"
        >
          <v-icon start>mdi-shield-check</v-icon>
          I Understand
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import {ref, computed, watch, onMounted, nextTick} from 'vue'
import {useLegalStore} from '@/stores/legal'
import {useScrollTracking} from '@/composables/legal/useScrollTracking'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'acknowledge'])

const legalStore = useLegalStore()
const {hasScrolledToBottom, checkScrollPosition, startTracking, setScrollContainer} = useScrollTracking()

const scrollElement = ref(null)

const dialog = computed({
  get: () => props.modelValue,
  set: (value) => {
    emit('update:modelValue', value)
    if (!value) {
      legalStore.closePrivacyDialog()
    }
  }
})

const lastUpdated = ref('December 15, 2024')

const onScroll = (event) => {
  checkScrollPosition()
}

const linkScrollElement = async () => {
  await nextTick()

  if (scrollElement.value) {
    let domElement = scrollElement.value

    if (domElement.$el) {
      domElement = domElement.$el
    }

    setScrollContainer(domElement)
  }
}

onMounted(() => {
  linkScrollElement()
})

watch(dialog, async (newValue) => {
  if (newValue) {
    legalStore.setPrivacyOpened()
    startTracking()

    setTimeout(() => {
      linkScrollElement()
    }, 150)
  }
})

watch(hasScrolledToBottom, (newValue) => {
  if (newValue) {
    legalStore.setPrivacyScrolledToBottom()
  }
})

const closeModal = () => {
  dialog.value = false
}

const acknowledgePolicy = () => {
  if (legalStore.canAcknowledgePrivacy) {
    legalStore.acknowledgePrivacy()
    emit('acknowledge')
    closeModal()
  }
}
</script>

<style scoped>
.privacy-modal {
  border-radius: 16px;
  overflow: hidden;
}

.privacy-header {
  background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%);
  color: white;
  padding: 20px 24px;
  position: sticky;
  top: 0;
  z-index: 1;
}

.privacy-title {
  font-size: 1.375rem;
  font-weight: 600;
  margin-left: 8px;
}

.reading-progress {
  margin-right: 12px;
}

.privacy-content {
  padding: 24px;
  max-height: 600px;
  background: #f8f9fa;
}

.privacy-text {
  max-width: 100%;
  line-height: 1.7;
}

.effective-date {
  margin-bottom: 24px;
  text-align: center;
}

.privacy-section {
  margin-bottom: 28px;
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s ease;
  border-left: 4px solid #4CAF50;
}

.privacy-section:hover {
  transform: translateY(-2px);
}

.section-title {
  color: #333;
  font-size: 1.125rem;
  font-weight: 600;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 2px solid #4CAF50;
}

.section-text {
  color: #555;
  font-size: 0.95rem;
  margin: 0;
  text-align: justify;
}

.privacy-actions {
  padding: 16px 24px;
  background: #e8f5e8;
}

.time-indicator {
  display: flex;
  align-items: center;
}

:deep(.v-theme--dark) .privacy-content {
  background: #1e1e1e;
}

:deep(.v-theme--dark) .privacy-section {
  background: #2d2d2d;
  box-shadow: 0 2px 8px rgba(255, 255, 255, 0.05);
  border-left-color: #66BB6A;
}

:deep(.v-theme--dark) .section-title {
  color: #fff;
  border-bottom-color: #66BB6A;
}

:deep(.v-theme--dark) .section-text {
  color: #ccc;
}

:deep(.v-theme--dark) .privacy-actions {
  background: #2d2d2d;
}
</style>