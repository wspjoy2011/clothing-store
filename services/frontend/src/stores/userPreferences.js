import {defineStore} from 'pinia'

export const useUserPreferencesStore = defineStore('userPreferences', {
    state: () => ({
        itemsPerPage: 12,
        theme: 'light',
    }),

    actions: {
        setItemsPerPage(count) {
            const validValues = [8, 12, 16, 20];
            if (validValues.includes(count)) {
                this.itemsPerPage = count;
            }
        },
        setTheme(theme) {
            if (theme === 'light' || theme === 'dark') {
                this.theme = theme;
            }
        },
    },
    persist: {
        key: 'user-preferences',
        storage: localStorage,
    }
});
