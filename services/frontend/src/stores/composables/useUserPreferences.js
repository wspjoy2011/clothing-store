import {THEMES, ITEMS_PER_PAGE_OPTIONS, DEFAULT_ITEMS_PER_PAGE} from '@/constants';

/**
 * Create initial state for user preferences store
 * @returns {Object} Initial user preferences state
 */
export function createInitialPreferencesState() {
    return {
        itemsPerPage: DEFAULT_ITEMS_PER_PAGE,
        theme: 'light',
    };
}

/**
 * Create actions for user preferences
 * @returns {Object} User preferences actions
 */
export function createPreferencesActions() {
    return {
        setItemsPerPage(count) {
            if (ITEMS_PER_PAGE_OPTIONS.includes(count)) {
                this.itemsPerPage = count;
            }
        },

        setTheme(theme) {
            if (THEMES.includes(theme)) {
                this.theme = theme;
            }
        },

        resetPreferences() {
            Object.assign(this, createInitialPreferencesState());
        }
    };
}
