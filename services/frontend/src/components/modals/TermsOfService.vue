<template>
  <v-dialog v-model="dialog" max-width="800" scrollable persistent>
    <v-card class="terms-modal">
      <v-card-title class="terms-header">
        <v-icon start icon="mdi-file-document-outline" size="28"></v-icon>
        <span class="terms-title">Terms of Service</span>
        <v-spacer></v-spacer>
        <div class="reading-progress">
          <v-chip
              :color="hasScrolledToBottom ? 'white' : 'orange'"
              size="small"
              variant="flat"
              :class="{ 'text-blue-darken-3': hasScrolledToBottom }"
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
          class="terms-content"
          @scroll="onScroll"
      >
        <div class="terms-text">
          <div class="effective-date">
            <v-chip color="primary" size="small" variant="tonal">
              Effective Date: {{ effectiveDate }}
            </v-chip>
          </div>

          <section class="terms-section">
            <h3 class="section-title">1. Acceptance of Terms</h3>
            <p class="section-text">
              Welcome to StyleShop! By accessing and using our e-commerce platform, you acknowledge
              that you have read, understood, and agree to be bound by these Terms of Service.
              These terms govern your relationship with StyleShop and your use of our services,
              including browsing products, making purchases, and accessing your account.
              If you do not agree with any part of these terms, please discontinue use of our platform immediately.
            </p>
          </section>

          <section class="terms-section">
            <h3 class="section-title">2. User Accounts and Responsibilities</h3>
            <p class="section-text">
              To access certain features of StyleShop, you may be required to create an account.
              You are responsible for maintaining the confidentiality of your account credentials
              and for all activities that occur under your account. You agree to provide accurate,
              current, and complete information during registration and to update such information
              as necessary. StyleShop reserves the right to suspend or terminate accounts that
              violate these terms or engage in fraudulent activities.
            </p>
          </section>

          <section class="terms-section">
            <h3 class="section-title">3. Product Information and Purchases</h3>
            <p class="section-text">
              StyleShop strives to provide accurate product descriptions, images, and pricing information.
              However, we do not warrant that product descriptions or other content is entirely accurate,
              complete, or error-free. All purchases are subject to product availability and our acceptance
              of your order. We reserve the right to limit quantities, refuse orders, or discontinue
              products at any time. Prices are subject to change without notice, though we will honor
              the price displayed at the time of your order confirmation.
            </p>
          </section>

          <section class="terms-section">
            <h3 class="section-title">4. Limitation of Liability</h3>
            <p class="section-text">
              StyleShop and its affiliates shall not be liable for any indirect, incidental, special,
              consequential, or punitive damages arising from your use of our platform or services.
              Our total liability to you for any damages shall not exceed the amount paid by you for
              the specific product or service giving rise to the claim. This limitation applies regardless
              of the legal theory upon which the claim is based and even if we have been advised of the
              possibility of such damages.
            </p>
          </section>

          <section class="terms-section">
            <h3 class="section-title">5. Intellectual Property Rights</h3>
            <p class="section-text">
              All content on StyleShop, including but not limited to text, graphics, logos, images,
              and software, is the property of StyleShop or its content suppliers and is protected
              by copyright, trademark, and other intellectual property laws. You may not reproduce,
              distribute, modify, or create derivative works from any content without our express
              written permission.
            </p>
          </section>

          <section class="terms-section">
            <h3 class="section-title">6. Payment and Billing Terms</h3>
            <p class="section-text">
              Payment for all purchases must be made at the time of order placement using accepted
              payment methods. We reserve the right to refuse or cancel orders at our discretion.
              All prices are subject to applicable taxes and shipping charges. Billing disputes must
              be reported within 30 days of the transaction date. Refunds and returns are subject
              to our return policy as outlined on our website.
            </p>
          </section>
        </div>
      </v-card-text>

      <v-divider></v-divider>

      <v-card-actions class="terms-actions">
        <div class="time-indicator">
          <v-chip
              size="small"
              variant="text"
              :color="legalStore.canAcceptTerms ? 'success' : 'grey'"
          >
            <v-icon start size="small">mdi-clock-outline</v-icon>
            {{ Math.floor(legalStore.termsTimeSpent / 1000) }}s / {{ Math.floor(legalStore.termsMinReadTime / 1000) }}s
          </v-chip>
        </div>
        <v-spacer></v-spacer>
        <v-btn color="grey" variant="text" @click="closeModal">
          Cancel
        </v-btn>
        <v-btn
            color="primary"
            variant="flat"
            :disabled="!legalStore.canAcceptTerms"
            @click="acceptTerms"
        >
          <v-icon start>mdi-check</v-icon>
          I Accept
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

const emit = defineEmits(['update:modelValue', 'accept'])

const legalStore = useLegalStore()
const {hasScrolledToBottom, checkScrollPosition, startTracking, setScrollContainer} = useScrollTracking()

const scrollElement = ref(null)

const dialog = computed({
  get: () => props.modelValue,
  set: (value) => {
    emit('update:modelValue', value)
    if (!value) {
      legalStore.closeTermsDialog()
    }
  }
})

const effectiveDate = ref('January 1, 2025')

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
    legalStore.setTermsOpened()
    startTracking()

    setTimeout(() => {
      linkScrollElement()
    }, 150)
  }
})

watch(hasScrolledToBottom, (newValue) => {
  if (newValue) {
    legalStore.setTermsScrolledToBottom()
  }
})

const closeModal = () => {
  dialog.value = false
}

const acceptTerms = () => {
  if (legalStore.canAcceptTerms) {
    legalStore.acceptTerms()
    emit('accept')
    closeModal()
  }
}
</script>

<style scoped>
.terms-modal {
  border-radius: 16px;
  overflow: hidden;
}

.terms-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px 24px;
  position: sticky;
  top: 0;
  z-index: 1;
}

.terms-title {
  font-size: 1.375rem;
  font-weight: 600;
  margin-left: 8px;
}

.reading-progress {
  margin-right: 12px;
}

.terms-content {
  padding: 24px;
  max-height: 600px;
  background: #fafafa;
}

.terms-text {
  max-width: 100%;
  line-height: 1.7;
}

.effective-date {
  margin-bottom: 24px;
  text-align: center;
}

.terms-section {
  margin-bottom: 28px;
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s ease;
}

.terms-section:hover {
  transform: translateY(-2px);
}

.section-title {
  color: #333;
  font-size: 1.125rem;
  font-weight: 600;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 2px solid #667eea;
}

.section-text {
  color: #555;
  font-size: 0.95rem;
  margin: 0;
  text-align: justify;
}

.terms-actions {
  padding: 16px 24px;
  background: #f5f5f5;
}

.time-indicator {
  display: flex;
  align-items: center;
}

:deep(.v-theme--dark) .terms-content {
  background: #1e1e1e;
}

:deep(.v-theme--dark) .terms-section {
  background: #2d2d2d;
  box-shadow: 0 2px 8px rgba(255, 255, 255, 0.05);
}

:deep(.v-theme--dark) .section-title {
  color: #fff;
}

:deep(.v-theme--dark) .section-text {
  color: #ccc;
}

:deep(.v-theme--dark) .terms-actions {
  background: #2d2d2d;
}
</style>
