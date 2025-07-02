import {defineStore} from 'pinia';

import {
    createInitialPreferencesState,
    createPreferencesActions
} from './composables';

export const useUserPreferencesStore = defineStore('userPreferences', {
    state: () => createInitialPreferencesState(),

    actions: {
        ...createPreferencesActions()
    },

    persist: {
        key: 'user-preferences',
        storage: localStorage,
    }
});
