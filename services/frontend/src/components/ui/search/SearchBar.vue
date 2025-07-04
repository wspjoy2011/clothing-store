<template>
  <div class="search-wrapper">
    <v-btn
        icon
        @click="toggleSearch"
        class="search-icon-btn"
    >
      <v-icon>mdi-magnify</v-icon>
    </v-btn>

    <v-dialog
        v-model="isExpanded"
        content-class="search-dialog"
        fullscreen
        transition="dialog-top-transition"
        scrim="false"
    >
      <v-card class="search-overlay" flat>
        <v-toolbar flat class="search-toolbar">
          <v-container>
            <div class="d-flex align-center">
              <div class="search-container flex-grow-1" ref="searchContainer">
                <v-text-field
                    v-model="searchQuery"
                    placeholder="Search products..."
                    variant="solo"
                    density="compact"
                    hide-details
                    :bg-color="isDarkTheme ? 'grey-darken-3' : 'grey-lighten-4'"
                    class="search-input"
                    @keyup.enter="handleSearch"
                    @keydown.down.prevent="navigateSuggestions(1)"
                    @keydown.up.prevent="navigateSuggestions(-1)"
                    @keydown.escape="handleEscape"
                    ref="searchInput"
                    autofocus
                >
                  <template v-slot:prepend>
                    <v-icon>mdi-magnify</v-icon>
                  </template>
                  <template v-slot:append>
                    <v-progress-circular
                        v-if="isLoading || suggestionsLoading"
                        indeterminate
                        size="20"
                        width="2"
                        color="primary"
                        class="mr-2"
                    ></v-progress-circular>
                    <v-btn
                        v-else-if="searchQuery"
                        icon="mdi-close"
                        size="small"
                        variant="text"
                        @click="clearSearch"
                    ></v-btn>
                  </template>
                </v-text-field>
              </div>

              <v-btn
                  icon
                  class="ml-2"
                  @click="isExpanded = false"
              >
                <v-icon>mdi-close</v-icon>
              </v-btn>
            </div>
          </v-container>
        </v-toolbar>

        <div class="search-backdrop" @click="isExpanded = false"></div>
      </v-card>
    </v-dialog>

    <!-- Autocomplete suggestions -->
    <teleport to="body">
      <v-card
          v-if="showSuggestions && suggestions.length > 0 && suggestionPosition"
          class="suggestions-list-portal"
          elevation="8"
          :style="suggestionPosition"
      >
        <v-list density="compact">
          <v-list-item
              v-for="(suggestion, index) in suggestions"
              :key="suggestion"
              :class="{ 'suggestion-active': index === selectedSuggestionIndex }"
              @click="selectSuggestion(suggestion)"
              @mouseenter="selectedSuggestionIndex = index"
          >
            <template v-slot:prepend>
              <v-icon size="20" class="mr-2">mdi-magnify</v-icon>
            </template>
            <v-list-item-title>{{ suggestion }}</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-card>
    </teleport>
  </div>
</template>

<script setup>
import {computed, nextTick, onMounted, onUnmounted, ref, watch} from 'vue';
import {useTheme} from 'vuetify';
import {useCatalogStore} from '@/stores/catalog';
import {useRoute, useRouter} from 'vue-router';
import {useDebounce} from '@/composables/useDebounce';
import catalogService from '@/services/catalogService';

const searchQuery = ref('');
const isExpanded = ref(false);
const isLoading = ref(false);
const searchInput = ref(null);
const searchContainer = ref(null);
const catalogStore = useCatalogStore();
const theme = useTheme();
const router = useRouter();
const route = useRoute();

const suggestions = ref([]);
const suggestionsLoading = ref(false);
const showSuggestions = ref(false);
const selectedSuggestionIndex = ref(-1);
const suggestionPosition = ref(null);

const {debouncedValue: debouncedQuery, cancel: cancelDebounce} = useDebounce(searchQuery, 300);

const isDarkTheme = computed(() => {
  return theme.global.current.value.dark;
});

const updateSuggestionPosition = () => {
  if (!searchContainer.value || !isExpanded.value) {
    suggestionPosition.value = null;
    return;
  }

  const container = searchContainer.value;
  const rect = container.getBoundingClientRect();

  suggestionPosition.value = {
    position: 'fixed',
    top: `${rect.bottom + 4}px`,
    left: `${rect.left}px`,
    right: `${window.innerWidth - rect.right}px`,
    zIndex: 2500
  };
};

watch(isExpanded, (expanded) => {
  if (expanded) {
    searchQuery.value = route.query.q || catalogStore.searchQuery || '';

    nextTick(() => {
      searchInput.value?.focus();
      updateSuggestionPosition();
    });
  } else {
    suggestionPosition.value = null;
    hideSuggestions();
  }
});

watch(debouncedQuery, async (newQuery) => {
  if (!isExpanded.value) return;

  if (!newQuery || newQuery.trim().length === 0) {
    suggestions.value = [];
    showSuggestions.value = false;
    selectedSuggestionIndex.value = -1;
    return;
  }

  if (newQuery.trim().length < 1) {
    return;
  }

  await fetchSuggestions(newQuery.trim());
});

watch(searchQuery, () => {
  if (suggestions.value.length > 0) {
    showSuggestions.value = true;
    updateSuggestionPosition();
  }
  selectedSuggestionIndex.value = -1;
});

const handleResize = () => {
  if (showSuggestions.value) {
    updateSuggestionPosition();
  }
};

onMounted(() => {
  window.addEventListener('resize', handleResize);
  window.addEventListener('scroll', handleResize);
});

onUnmounted(() => {
  cancelDebounce();
  window.removeEventListener('resize', handleResize);
  window.removeEventListener('scroll', handleResize);
});

const fetchSuggestions = async (query) => {
  try {
    suggestionsLoading.value = true;
    const result = await catalogService.getProductSuggestions(query, 8);
    suggestions.value = result;
    showSuggestions.value = result.length > 0;
    selectedSuggestionIndex.value = -1;
    updateSuggestionPosition();
  } catch (error) {
    console.error('Error fetching suggestions:', error);
    suggestions.value = [];
    showSuggestions.value = false;
  } finally {
    suggestionsLoading.value = false;
  }
};

const navigateSuggestions = (direction) => {
  if (!showSuggestions.value || suggestions.value.length === 0) return;

  const newIndex = selectedSuggestionIndex.value + direction;

  if (newIndex < -1) {
    selectedSuggestionIndex.value = suggestions.value.length - 1;
  } else if (newIndex >= suggestions.value.length) {
    selectedSuggestionIndex.value = -1;
  } else {
    selectedSuggestionIndex.value = newIndex;
  }
};

const selectSuggestion = (suggestion) => {
  searchQuery.value = suggestion;
  hideSuggestions();
  handleSearch();
};

const hideSuggestions = () => {
  showSuggestions.value = false;
  selectedSuggestionIndex.value = -1;
  suggestionPosition.value = null;
};

const handleEscape = () => {
  if (showSuggestions.value) {
    hideSuggestions();
  } else {
    isExpanded.value = false;
  }
};

const toggleSearch = () => {
  isExpanded.value = !isExpanded.value;

  if (!isExpanded.value) {
    if (!searchQuery.value.trim()) {
      clearSearch();
    }
  }
};

const clearSearch = () => {
  searchQuery.value = '';
  hideSuggestions();
  cancelDebounce();

  if (route.name === 'catalog') {
    isLoading.value = true;

    const query = {...route.query};
    delete query.q;
    delete query.page;

    catalogStore.clearSearchQuery();

    router.push({
      name: 'catalog',
      query: query
    }).then(() => {
      catalogStore.fetchProducts(1);

      setTimeout(() => {
        isLoading.value = false;
      }, 300);
    });
  } else {
    catalogStore.clearSearchQuery();
  }

  searchInput.value?.focus();
};

const handleSearch = () => {
  if (selectedSuggestionIndex.value >= 0 && suggestions.value[selectedSuggestionIndex.value]) {
    searchQuery.value = suggestions.value[selectedSuggestionIndex.value];
  }

  if (!searchQuery.value.trim() && !catalogStore.searchQuery) {
    isExpanded.value = false;
    return;
  }

  hideSuggestions();
  isLoading.value = true;
  const trimmedQuery = searchQuery.value.trim();

  const query = {...route.query};

  if (trimmedQuery) {
    query.q = trimmedQuery;
    delete query.page;
  } else {
    delete query.q;
  }

  catalogStore.setSearchQuery(trimmedQuery);

  if (route.name === 'catalog') {
    catalogStore.fetchFilters().then(() => {
      router.push({
        name: 'catalog',
        query: query
      }).then(() => {
        catalogStore.fetchProducts(1);

        setTimeout(() => {
          isLoading.value = false;
          isExpanded.value = false;
        }, 500);
      });
    });
  } else {
    router.push({
      name: 'catalog',
      query: query
    }).then(() => {
      setTimeout(() => {
        isLoading.value = false;
        isExpanded.value = false;
      }, 500);
    });
  }
};
</script>

<style scoped>
.search-wrapper {
  position: relative;
  display: inline-block;
}

.search-dialog {
  box-shadow: none;
  background: transparent;
}

.search-overlay {
  box-shadow: none;
  background: transparent;
}

.search-toolbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
}

.search-container {
  position: relative;
}

.suggestions-list-portal {
  max-height: 300px;
  overflow-y: auto;
  border-radius: 4px;
}

.suggestion-active {
  background-color: rgba(25, 118, 210, 0.1) !important;
}

:deep(.v-theme--dark) .suggestion-active {
  background-color: rgba(144, 202, 249, 0.15) !important;
}

:deep(.v-list-item) {
  cursor: pointer;
  transition: background-color 0.2s ease;
}

:deep(.v-list-item:hover) {
  background-color: rgba(0, 0, 0, 0.04);
}

:deep(.v-theme--dark .v-list-item:hover) {
  background-color: rgba(255, 255, 255, 0.08);
}

.search-backdrop {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: -1;
  cursor: pointer;
}

:deep(.v-theme--light) .search-toolbar {
  background: rgba(255, 255, 255, 0.98);
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
  backdrop-filter: blur(10px);
}

:deep(.v-theme--dark) .search-toolbar {
  background: rgba(30, 30, 30, 0.98);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(10px);
}

:deep(.v-theme--light) .search-backdrop {
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(5px);
}

:deep(.v-theme--dark) .search-backdrop {
  background: rgba(30, 30, 30, 0.6);
  backdrop-filter: blur(5px);
}

.search-input {
  border-radius: 4px;
}

:deep(.dialog-top-transition-enter-active),
:deep(.dialog-top-transition-leave-active) {
  transition: all 0.2s ease-in-out;
}

:deep(.dialog-top-transition-enter-from),
:deep(.dialog-top-transition-leave-to) {
  transform: translateY(-30px);
  opacity: 0;
}
</style>
