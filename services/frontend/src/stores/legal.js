import {defineStore} from 'pinia';
import {
    createInitialLegalState,
    createLegalGetters,
    createLegalActions,
    getLegalPersistPaths
} from './helpers';

export const useLegalStore = defineStore('legal', {
    state: () => createInitialLegalState(),

    getters: {
        ...createLegalGetters()
    },

    actions: {
        ...createLegalActions()
    },

    persist: {
        key: 'legal-store',
        storage: localStorage,
        paths: getLegalPersistPaths()
    }
});
