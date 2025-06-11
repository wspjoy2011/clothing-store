import {defineStore} from 'pinia'

export const useLegalStore = defineStore('legal', {
    state: () => ({
        termsScrolledToBottom: false,
        privacyScrolledToBottom: false,
        termsAccepted: false,
        privacyAcknowledged: false,
        termsOpenedAt: null,
        privacyOpenedAt: null,
        termsMinReadTime: 2000,
        privacyMinReadTime: 2000,
        showTermsDialog: false,
        showPrivacyDialog: false,
        termsCurrentTime: 0,
        privacyCurrentTime: 0
    }),

    getters: {
        canAcceptTerms: (state) => {
            const result = state.termsScrolledToBottom && state.termsCurrentTime >= state.termsMinReadTime
            return result
        },

        canAcknowledgePrivacy: (state) => {
            const result = state.privacyScrolledToBottom && state.privacyCurrentTime >= state.privacyMinReadTime
            return result
        },

        hasReadBothDocuments: (state) => {
            return state.termsAccepted && state.privacyAcknowledged
        },

        termsTimeSpent: (state) => state.termsCurrentTime,
        privacyTimeSpent: (state) => state.privacyCurrentTime
    },

    actions: {
        setTermsOpened() {
            this.termsOpenedAt = Date.now()
            this.termsScrolledToBottom = false
            this.termsCurrentTime = 0
            this.startTermsTimer()
        },

        setPrivacyOpened() {
            this.privacyOpenedAt = Date.now()
            this.privacyScrolledToBottom = false
            this.privacyCurrentTime = 0
            this.startPrivacyTimer()
        },

        startTermsTimer() {
            if (this.termsTimer) {
                clearInterval(this.termsTimer)
            }

            this.termsTimer = setInterval(() => {
                if (this.termsOpenedAt) {
                    this.termsCurrentTime = Date.now() - this.termsOpenedAt
                }
            }, 100)
        },

        startPrivacyTimer() {
            if (this.privacyTimer) {
                clearInterval(this.privacyTimer)
            }

            this.privacyTimer = setInterval(() => {
                if (this.privacyOpenedAt) {
                    this.privacyCurrentTime = Date.now() - this.privacyOpenedAt
                }
            }, 100)
        },

        stopTermsTimer() {
            if (this.termsTimer) {
                clearInterval(this.termsTimer)
                this.termsTimer = null
            }
        },

        stopPrivacyTimer() {
            if (this.privacyTimer) {
                clearInterval(this.privacyTimer)
                this.privacyTimer = null
            }
        },

        setTermsScrolledToBottom() {
            this.termsScrolledToBottom = true
        },

        setPrivacyScrolledToBottom() {
            this.privacyScrolledToBottom = true
        },

        acceptTerms() {
            if (this.canAcceptTerms) {
                this.termsAccepted = true
                this.stopTermsTimer()
            }
        },

        acknowledgePrivacy() {
            if (this.canAcknowledgePrivacy) {
                this.privacyAcknowledged = true
                this.stopPrivacyTimer()
            }
        },

        openTermsDialog() {
            this.showTermsDialog = true
        },

        closeTermsDialog() {
            this.showTermsDialog = false
            this.stopTermsTimer()
        },

        openPrivacyDialog() {
            this.showPrivacyDialog = true
        },

        closePrivacyDialog() {
            this.showPrivacyDialog = false
            this.stopPrivacyTimer()
        },

        resetLegalState() {
            this.termsScrolledToBottom = false
            this.privacyScrolledToBottom = false
            this.termsAccepted = false
            this.privacyAcknowledged = false
            this.termsOpenedAt = null
            this.privacyOpenedAt = null
            this.termsCurrentTime = 0
            this.privacyCurrentTime = 0
            this.showTermsDialog = false
            this.showPrivacyDialog = false
            this.stopTermsTimer()
            this.stopPrivacyTimer()
        }
    },

    persist: {
        key: 'legal-store',
        storage: localStorage,
        paths: ['termsAccepted', 'privacyAcknowledged']
    }
})
