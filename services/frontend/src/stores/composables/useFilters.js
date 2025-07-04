/**
 * Creates filter actions for stores
 * @returns {Object} Filter actions
 */
export function createFiltersActions() {
    return {
        /**
         * Set active filters
         * @param {Object} filters - Filters object
         */
        setActiveFilters(filters) {
            Object.assign(this.activeFilters, filters);
        },

        /**
         * Set available filters
         * @param {Object} filters - Available filters object
         */
        setAvailableFilters(filters) {
            this.availableFilters = filters || {gender: null, year: null};
        },

        /**
         * Load filters from query parameters
         * @param {Object} query - Route query object
         */
        loadFiltersFromQuery(query) {
            this.activeFilters.gender = query.gender || null;
            this.activeFilters.min_year = query.min_year ? parseInt(query.min_year) : null;
            this.activeFilters.max_year = query.max_year ? parseInt(query.max_year) : null;
            this.searchQuery = query.q || '';
        },

        /**
         * Clear gender filter
         */
        clearGenderFilter() {
            this.activeFilters.gender = null;
        },

        /**
         * Clear year filter
         */
        clearYearFilter() {
            this.activeFilters.min_year = null;
            this.activeFilters.max_year = null;
        },

        /**
         * Clear all filters
         */
        clearAllFilters() {
            this.resetFilters();
        },

        /**
         * Reset filters to initial state
         */
        resetFilters() {
            this.activeFilters = {
                gender: null,
                min_year: null,
                max_year: null
            };
            this.searchQuery = '';
        },

        /**
         * Set search query
         * @param {string} query - Search query
         */
        setSearchQuery(query) {
            this.searchQuery = query || '';
        },

        /**
         * Clear search query
         */
        clearSearchQuery() {
            this.searchQuery = '';
        },

        /**
         * Clear search - alias for clearSearchQuery for backward compatibility
         */
        clearSearch() {
            this.clearSearchQuery();
        },

        /**
         * Toggle filter drawer
         * @param {boolean} isOpen - Drawer state
         */
        toggleFilterDrawer(isOpen = null) {
            if (isOpen !== null) {
                this.isFilterDrawerOpen = isOpen;
            } else {
                this.isFilterDrawerOpen = !this.isFilterDrawerOpen;
            }
        }
    };
}

/**
 * Creates filter getters for stores
 * @returns {Object} Filter getters
 */
export function createFiltersGetters() {
    return {
        hasActiveFilters(state) {
            return state.activeFiltersCount > 0;
        },

        activeFiltersCount(state) {
            let count = 0;
            if (state.activeFilters.gender) count++;
            if (state.activeFilters.min_year || state.activeFilters.max_year) count++;
            if (state.searchQuery && state.searchQuery.trim()) count++;
            return count;
        },

        hasAvailableFilters(state) {
            return state.availableFilters &&
                (state.availableFilters.gender || state.availableFilters.year);
        }
    };
}

/**
 * Creates initial filters state
 * @returns {Object} Initial filters state
 */
export function createInitialFiltersState() {
    return {
        activeFilters: {
            gender: null,
            min_year: null,
            max_year: null
        },
        availableFilters: {
            gender: null,
            year: null
        },
        searchQuery: '',
        filtersLoading: false,
        filtersError: null,
        isFilterDrawerOpen: false
    };
}
