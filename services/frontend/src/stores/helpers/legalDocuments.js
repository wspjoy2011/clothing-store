/**
 * Legal documents helper for managing terms and privacy policy states
 */

/**
 * Create initial state for a legal document
 * @param {number} minReadTime - Minimum time to read the document in milliseconds
 * @returns {Object} Initial document state
 */
export function createDocumentState(minReadTime = 2000) {
    return {
        scrolledToBottom: false,
        accepted: false,
        openedAt: null,
        currentTime: 0,
        minReadTime,
        showDialog: false,
        timer: null
    };
}

/**
 * Create initial state for legal documents store
 * @returns {Object} Initial legal documents state
 */
export function createInitialLegalState() {
    return {
        documents: {
            terms: createDocumentState(2000),
            privacy: createDocumentState(2000)
        }
    };
}

/**
 * Create getters for legal documents
 * @returns {Object} Legal documents getters
 */
export function createLegalGetters() {
    return {
        canAcceptDocument: (state) => (type) => {
            const doc = state.documents[type];
            return doc.scrolledToBottom && doc.currentTime >= doc.minReadTime;
        },

        canAcceptTerms(state) {
            const doc = state.documents.terms;
            return doc.scrolledToBottom && doc.currentTime >= doc.minReadTime;
        },

        canAcknowledgePrivacy(state) {
            const doc = state.documents.privacy;
            return doc.scrolledToBottom && doc.currentTime >= doc.minReadTime;
        },

        hasReadBothDocuments(state) {
            return state.documents.terms.accepted && state.documents.privacy.accepted;
        },

        documentTimeSpent: (state) => (type) => {
            return state.documents[type].currentTime;
        },

        termsTimeSpent(state) {
            return state.documents.terms.currentTime;
        },

        privacyTimeSpent(state) {
            return state.documents.privacy.currentTime;
        },

        termsMinReadTime(state) {
            return state.documents.terms.minReadTime;
        },

        privacyMinReadTime(state) {
            return state.documents.privacy.minReadTime;
        },

        termsAccepted(state) {
            return state.documents.terms.accepted;
        },

        privacyAcknowledged(state) {
            return state.documents.privacy.accepted;
        },

        isDocumentDialogOpen: (state) => (type) => {
            return state.documents[type].showDialog;
        },

        showTermsDialog(state) {
            return state.documents.terms.showDialog;
        },

        showPrivacyDialog(state) {
            return state.documents.privacy.showDialog;
        }
    };
}

/**
 * Create actions for legal documents
 * @returns {Object} Legal documents actions
 */
export function createLegalActions() {
    return {
        setDocumentOpened(type) {
            const doc = this.documents[type];
            doc.openedAt = Date.now();
            doc.scrolledToBottom = false;
            doc.currentTime = 0;
            this.startDocumentTimer(type);
        },

        startDocumentTimer(type) {
            const doc = this.documents[type];

            if (doc.timer) {
                clearInterval(doc.timer);
            }

            doc.timer = setInterval(() => {
                if (doc.openedAt) {
                    doc.currentTime = Date.now() - doc.openedAt;
                }
            }, 100);
        },

        stopDocumentTimer(type) {
            const doc = this.documents[type];

            if (doc.timer) {
                clearInterval(doc.timer);
                doc.timer = null;
            }
        },

        setDocumentScrolledToBottom(type) {
            this.documents[type].scrolledToBottom = true;
        },

        acceptDocument(type) {
            const doc = this.documents[type];
            if (doc.scrolledToBottom && doc.currentTime >= doc.minReadTime) {
                doc.accepted = true;
                this.stopDocumentTimer(type);
            }
        },

        openDocumentDialog(type) {
            this.documents[type].showDialog = true;
        },

        closeDocumentDialog(type) {
            this.documents[type].showDialog = false;
            this.stopDocumentTimer(type);
        },

        // Convenience methods for specific documents
        setTermsOpened() {
            this.setDocumentOpened('terms');
        },

        setPrivacyOpened() {
            this.setDocumentOpened('privacy');
        },

        startTermsTimer() {
            this.startDocumentTimer('terms');
        },

        startPrivacyTimer() {
            this.startDocumentTimer('privacy');
        },

        stopTermsTimer() {
            this.stopDocumentTimer('terms');
        },

        stopPrivacyTimer() {
            this.stopDocumentTimer('privacy');
        },

        setTermsScrolledToBottom() {
            this.setDocumentScrolledToBottom('terms');
        },

        setPrivacyScrolledToBottom() {
            this.setDocumentScrolledToBottom('privacy');
        },

        acceptTerms() {
            this.acceptDocument('terms');
        },

        acknowledgePrivacy() {
            this.acceptDocument('privacy');
        },

        openTermsDialog() {
            this.openDocumentDialog('terms');
        },

        closeTermsDialog() {
            this.closeDocumentDialog('terms');
        },

        openPrivacyDialog() {
            this.openDocumentDialog('privacy');
        },

        closePrivacyDialog() {
            this.closeDocumentDialog('privacy');
        },

        resetLegalState() {
            Object.keys(this.documents).forEach(type => {
                this.stopDocumentTimer(type);
            });

            const initialState = createInitialLegalState();
            Object.assign(this.documents, initialState.documents);
        }
    };
}

/**
 * Get persistent paths for legal store
 * @returns {string[]} Paths to persist in localStorage
 */
export function getLegalPersistPaths() {
    return [
        'documents.terms.accepted',
        'documents.privacy.accepted'
    ];
}
