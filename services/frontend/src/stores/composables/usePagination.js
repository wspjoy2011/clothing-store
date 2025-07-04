/**
 * Creates pagination state for stores
 * @returns {Object} Pagination state
 */
export function createPaginationState() {
    return {
        currentPage: 1,
        totalPages: 0,
        totalItems: 0,
        itemsPerPage: 12
    };
}

/**
 * Creates pagination actions for stores
 * @returns {Object} Pagination actions
 */
export function createPaginationActions() {
    return {
        /**
         * Set pagination data
         * @param {Object} data - Pagination data
         */
        setPaginationData(data) {
            this.currentPage = data.currentPage || 1;
            this.totalPages = data.totalPages || 0;
            this.totalItems = data.totalItems || 0;
        },

        /**
         * Set current page
         * @param {number} page - Page number
         */
        setCurrentPage(page) {
            this.currentPage = page;
        },

        /**
         * Set items per page
         * @param {number} count - Items per page
         */
        setItemsPerPage(count) {
            this.itemsPerPage = count;
        },

        /**
         * Reset pagination
         */
        resetPagination() {
            this.currentPage = 1;
            this.totalPages = 0;
            this.totalItems = 0;
        }
    };
}

/**
 * Creates pagination getters for stores
 * @returns {Object} Pagination getters
 */
export function createPaginationGetters() {
    return {
        hasItems(state) {
            return state.totalPages > 0;
        },

        hasPagination(state) {
            return state.totalPages > 1;
        }
    };
}
