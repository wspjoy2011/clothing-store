import { nextTick } from 'vue';

/**
 * Initial filters state factory
 * @returns {Object} - Initial filters state
 */
export function createInitialFiltersState() {
    return {
        availableFilters: {
            gender: null,
            year: null
        },
        activeFilters: {
            gender: null,
            min_year: null,
            max_year: null
        },
        filtersLoading: false,
        filtersError: null,
        isFilterDrawerOpen: false,
        isUpdatingFilters: false,
        searchQuery: null
    };
}

/**
 * Create filters getters for store
 * @returns {Object} - Filters getters
 */
export function createFiltersGetters() {
    return {
        activeFiltersCount(state) {
            let count = 0;

            if (state.activeFilters.gender !== null) {
                count++;
            }

            if (
                state.availableFilters?.year &&
                ((state.activeFilters.min_year !== null &&
                        state.activeFilters.min_year !== state.availableFilters.year.min) ||
                    (state.activeFilters.max_year !== null &&
                        state.activeFilters.max_year !== state.availableFilters.year.max))
            ) {
                count++;
            }

            return count;
        },

        hasActiveFilters() {
            return this.activeFiltersCount > 0;
        }
    };
}

/**
 * Create filters actions for Pinia store
 * @returns {Object} - Filters actions
 */
export function createFiltersActions() {
    return {
        clearFilters() {
            const drawerWasOpen = this.isFilterDrawerOpen;

            this.isUpdatingFilters = true;

            this.activeFilters = {
                gender: null,
                min_year: null,
                max_year: null
            };

            nextTick(() => {
                this.isUpdatingFilters = false;

                if (drawerWasOpen) {
                    setTimeout(() => {
                        this.isFilterDrawerOpen = true;
                    }, 0);
                }
            });
        },

        clearSearch() {
            this.searchQuery = null;
        },

        setSearchQuery(query) {
            this.searchQuery = query?.trim() || null;
        },

        loadFiltersFromQuery(query) {
            this.isUpdatingFilters = true;

            this.activeFilters = {
                gender: query.gender || null,
                min_year: query.min_year ? parseInt(query.min_year) : null,
                max_year: query.max_year ? parseInt(query.max_year) : null
            };

            this.searchQuery = query.q?.trim() || null;

            nextTick(() => {
                this.isUpdatingFilters = false;
            });
        },

        toggleFilterDrawer(value = null) {
            if (value !== null) {
                this.isFilterDrawerOpen = value;
            } else {
                this.isFilterDrawerOpen = !this.isFilterDrawerOpen;
            }
        },

        resetFilters() {
            const filtersState = createInitialFiltersState();
            Object.assign(this, filtersState);
        }
    };
}
