import {defineStore} from 'pinia';

import {
    createInitialPreferencesState,
    createPreferencesActions
} from './composables';

export const useUserPreferencesStore = defineStore('userPreferences', {
    state: () => ({
        ...createInitialPreferencesState(),
        productOrdering: '-id'
    }),

    actions: {
        ...createPreferencesActions(),

        setProductOrdering(ordering) {
            this.productOrdering = ordering || '-id';
        }
    },

    persist: {
        key: 'user-preferences',
        storage: localStorage,
    }
});
